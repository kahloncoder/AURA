import os
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import numpy as np
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions
import requests
import wave
import tempfile
# REMOVED: import torch

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Global handlers and models ---
deepgram_client = None
cerebras_handler = None
active_sessions = {}
# REMOVED: VAD model globals
# --- End Globals ---


# RENAMED and SIMPLIFIED: This class now only handles saving the audio file.
class AudioHandler:
    def save_wav_from_base64(self, audio_base64, filename, sample_rate=16000):
        audio_bytes = base64.b64decode(audio_base64)

        # Write bytes directly (assume already WAV)
        with open(filename, 'wb') as f:
            f.write(audio_bytes)

        print(f"DEBUG: Wrote {len(audio_bytes)} bytes to {filename}")
        return audio_bytes

class DeepgramHandler:
    """Handle Deepgram STT and TTS"""
    
    def __init__(self, api_key, sample_rate=16000):
        # Accept either DEEPGRAM_API_KEY env var or explicit api_key
        # DeepgramClient accepts api_key=... per SDK docs
        self.client = DeepgramClient(api_key=api_key)
        self.sample_rate = sample_rate
    
    def transcribe(self, audio_file):
        """Convert speech to text using Deepgram SDK (sync)"""
        try:
            with open(audio_file, 'rb') as f:
                buffer = f.read()

            # --- Options: use model nova-2 with useful processing flags ---
            # Use the SDK's transcribe_file interface for pre-recorded audio
            response = self.client.listen.v1.media.transcribe_file(
                request=buffer,
                model="nova-2",
                smart_format=True,
                punctuate=True,
                diarize=True,
                numerals=True
            )

            # Debug: show full response structure (partial) safely
            try:
                # response may be an object with 'results' attr per SDK
                results = getattr(response, "results", None) or response.get("results", None)
            except Exception:
                results = None

            print(f"DEBUG: Deepgram response (results present?): {bool(results)}")

            # Extract transcript using SDK structure
            # Common path: response.results.channels[0].alternatives[0].transcript
            transcript = None
            try:
                if results:
                    channels = results.get("channels") if isinstance(results, dict) else getattr(results, "channels", None)
                    if channels and len(channels) > 0:
                        alternatives = channels[0].get("alternatives") if isinstance(channels[0], dict) else getattr(channels[0], "alternatives", None)
                        if alternatives and len(alternatives) > 0:
                            # alternative might be dict-like or object-like
                            alt0 = alternatives[0]
                            if isinstance(alt0, dict):
                                transcript = alt0.get("transcript")
                            else:
                                transcript = getattr(alt0, "transcript", None)
            except Exception as e:
                print(f"DEBUG: Error extracting transcript from response: {e}")

            # Fallback safer path if SDK returned object attributes
            if not transcript:
                try:
                    transcript = response.results.channels[0].alternatives[0].transcript
                except Exception:
                    transcript = None

            if transcript:
                return transcript.strip()

            print("DEBUG: Deepgram returned a response, but it contained no transcript.")
            return None
        
        except Exception as e:
            # Print full exception for debugging
            print(f"TRANSCRIPTION ERROR from Deepgram: {e}")
            return None
    
    def synthesize(self, text, voice="aura-asteria-en"):
        """Convert text to speech and return base64 (using Deepgram speak API)"""
        try:
            # Use speak.v1.audio.generate(...) as shown in SDK docs
            response = self.client.speak.v1.audio.generate(
                text=text,
                voice=voice,
                encoding="linear16",
                sample_rate=self.sample_rate
            )

            # The SDK returns an object with a .stream attribute (BytesIO-like).
            # Use .stream.getvalue() if present, otherwise attempt .stream.read()
            audio_bytes = None
            stream = getattr(response, "stream", None)
            if stream is not None:
                try:
                    # BytesIO-like
                    audio_bytes = stream.getvalue()
                except Exception:
                    try:
                        # file-like
                        audio_bytes = stream.read()
                    except Exception:
                        audio_bytes = None

            # Fallback: some responses expose .data or .raw bytes
            if audio_bytes is None:
                if hasattr(response, "data"):
                    audio_bytes = response.data
                elif isinstance(response, dict) and response.get("audio"):
                    # unlikely, but defensive
                    audio_bytes = response.get("audio")

            if not audio_bytes:
                print("DEBUG: Deepgram TTS returned no audio bytes")
                return None

            return base64.b64encode(audio_bytes).decode('utf-8')

        except Exception as e:
            print(f"TTS error: {e}")
            return None

class CerebrasHandler:
    """Handle Cerebras LLM API calls"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.cerebras.ai/v1/chat/completions"
        self.model = "llama3.3-70b"
    
    def chat(self, messages, temperature=0.7, max_tokens=500):
        """Make LLM API call"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        
        except Exception as e:
            print(f"LLM error: {e}")
            return None


class SessionManager:
    """Manage conversation sessions"""
    
    def __init__(self, room, duration_minutes):
        self.room = room
        self.start_time = datetime.now()
        self.duration = timedelta(minutes=duration_minutes)
        self.end_time = self.start_time + self.duration
        self.conversation_log = []
        self.context = []
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def is_expired(self):
        return datetime.now() >= self.end_time
    
    def remaining_time(self):
        remaining = self.end_time - datetime.now()
        return max(0, int(remaining.total_seconds()))
    
    def log_interaction(self, role, content):
        self.conversation_log.append({"timestamp": datetime.now().isoformat(), "role": role, "content": content})
    
    def process_user_input(self, user_text, llm_handler):
        """Process through multi-agent system"""
        agent_responses = []
        for agent in self.room['agents']:
            messages = [{"role": "system", "content": agent['system_prompt']}]
            for ctx in self.context[-6:]:
                messages.append(ctx)
            
            if agent_responses:
                context_text = f"User: {user_text}\n\nPrevious Agent Responses:\n" + "".join([f"Agent {i+1}: {resp}\n" for i, resp in enumerate(agent_responses)])
                messages.append({"role": "user", "content": context_text})
            else:
                messages.append({"role": "user", "content": user_text})
            
            response = llm_handler.chat(messages, temperature=agent['temperature'], max_tokens=200)
            if response:
                agent_responses.append(response)
        
        final_response = " ".join(agent_responses)
        self.context.extend([{"role": "user", "content": user_text}, {"role": "assistant", "content": final_response}])
        return final_response
    
    def save_log(self):
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir / f"aura_{self.room['name'].replace(' ', '_')}_{timestamp}.json"
        session_data = {
            "room": self.room['name'],
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "conversation": self.conversation_log
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)


def initialize_handlers():
    global deepgram_client, cerebras_handler

    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    if not deepgram_key or not cerebras_key:
        raise ValueError("API keys not found in .env file")

    deepgram_client = DeepgramHandler(deepgram_key)
    cerebras_handler = CerebrasHandler(cerebras_key)
    print("✅ Core handlers initialized successfully.")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    try:
        with open('rooms.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected:', request.sid)

@socketio.on('start_session')
def handle_start_session(data):
    try:
        with open('rooms.json', 'r', encoding='utf-8') as f:
            rooms = json.load(f)
        selected_room = rooms['rooms'][data.get('room_index', 0)]
        session = SessionManager(selected_room, selected_room['session_duration_minutes'])
        active_sessions[request.sid] = session
        greeting = selected_room.get('greeting', 'Hello! How can I help you today?')
        session.log_interaction('assistant', greeting)
        emit('session_started', {
            'room': selected_room['name'],
            'duration': selected_room['session_duration_minutes'],
            'agents': [a['name'] for a in selected_room['agents']],
            'greeting': greeting
        })
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('process_audio')
def handle_process_audio(data):
    session = active_sessions.get(request.sid)
    if not session:
        return emit('error', {'message': 'No active session'})
    if session.is_expired():
        return emit('session_expired', {'message': 'Session time limit reached'})
    
    temp_dir = tempfile.mkdtemp()
    try:
        audio_base64 = data.get('audio')
        audio_file = os.path.join(temp_dir, 'input.wav')

        audio_handler = AudioHandler()
        audio_bytes = audio_handler.save_wav_from_base64(audio_base64, audio_file)

        try:
            with wave.open(audio_file, 'rb') as wf:
                print(f"DEBUG: WAV file saved successfully.")
                print(f"  - Channels: {wf.getnchannels()}")
                print(f"  - Sample Width: {wf.getsampwidth()} bytes")
                print(f"  - Frame Rate: {wf.getframerate()} Hz")
                print(f"  - Frames: {wf.getnframes()}")
                print(f"  - Duration: {wf.getnframes() / wf.getframerate():.2f} seconds")
        except Exception as e:
            print(f"DEBUG: Error reading back WAV file: {e}")

        emit('status', {'message': 'Transcribing...', 'type': 'transcribing'})
        user_text = deepgram_client.transcribe(audio_file)
        
        if not user_text:
            if len(audio_bytes) < 2000:
                 return emit('status', {'message': 'Recording was empty.', 'type': 'vad_fail'})
            return emit('error', {'message': 'Could not understand audio'})

        session.log_interaction('user', user_text)
        emit('transcription', {'text': user_text})

        emit('status', {'message': 'Processing...', 'type': 'processing'})
        response = session.process_user_input(user_text, cerebras_handler)
        session.log_interaction('assistant', response)

        emit('status', {'message': 'Generating speech...', 'type': 'synthesizing'})
        audio_response = deepgram_client.synthesize(response)

        emit('response', {
            'text': response,
            'audio': audio_response,
            'remaining_time': session.remaining_time()
        })
    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': str(e)})
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

@socketio.on('end_session')
def handle_end_session():
    session = active_sessions.get(request.sid)
    if session:
        session.save_log()
        del active_sessions[request.sid]
    emit('session_ended', {'message': 'Session saved successfully'})


if __name__ == '__main__':
    try:
        initialize_handlers()
        print("✅ AURA Backend initialized")
        print("🌐 Starting server on http://localhost:5000")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Startup Error: {e}")

