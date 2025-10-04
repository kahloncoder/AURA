import os
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import wave
import tempfile
import subprocess
import shutil

import requests
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Globals
deepgram_client = None
cerebras_handler = None
active_sessions = {}

# ---------------- Audio Handling ---------------- #
class AudioHandler:
    """Handles audio file operations and normalizes to 16kHz mono PCM16 using ffmpeg."""

    def save_wav_from_base64(self, audio_base64, filename, sample_rate=16000):
        """Convert base64 audio to 16kHz mono WAV using ffmpeg"""
        try:
            audio_bytes = base64.b64decode(audio_base64)
            tmp_in = filename + ".in"

            # Write the raw input
            with open(tmp_in, "wb") as f:
                f.write(audio_bytes)

            # Use ffmpeg to convert to proper format
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", tmp_in,
                "-ac", "1",  # mono
                "-ar", str(sample_rate),  # 16kHz
                "-sample_fmt", "s16",  # 16-bit PCM
                "-f", "wav",  # force WAV format
                filename
            ]
            
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            
            # Read the converted file
            with open(filename, 'rb') as f:
                out_bytes = f.read()
            
            print(f"✅ Audio converted successfully: {len(out_bytes)} bytes")
            return out_bytes
            
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg error: {e.stderr.decode()}")
            return audio_bytes
        except Exception as e:
            print(f"❌ Audio conversion error: {e}")
            return audio_bytes
        finally:
            # Cleanup
            try: 
                os.remove(tmp_in)
            except: 
                pass

# ---------------- Deepgram ---------------- #
class DeepgramHandler:
    """Handle Deepgram STT and TTS"""
    
    def __init__(self, api_key, sample_rate=16000):
        self.client = DeepgramClient(api_key)
        self.sample_rate = sample_rate
    
    def transcribe(self, audio_file):
        try:
            with open(audio_file, 'rb') as f:
                buffer = f.read()
            
            print(f"🎤 Transcribing audio: {len(buffer)} bytes")
            
            options = PrerecordedOptions(
                model="nova-2", 
                smart_format=True, 
                language="en",
                encoding="linear16",
                sample_rate=16000 
            )

            response = self.client.listen.rest.v('1').transcribe_file({'buffer': buffer}, options)
            response_dict = response.to_dict()

            if (response_dict and response_dict.get('results') 
                and response_dict['results'].get('channels') 
                and len(response_dict['results']['channels']) > 0 
                and response_dict['results']['channels'][0].get('alternatives') 
                and len(response_dict['results']['channels'][0]['alternatives']) > 0):
                transcript = response_dict['results']['channels'][0]['alternatives'][0]['transcript']
                if transcript:
                    print(f"✅ Transcription: {transcript}")
                    return transcript.strip()
            
            print("⚠️ No transcription returned")
            return None
        
        except Exception as e:
            print(f"❌ TRANSCRIPTION ERROR from Deepgram: {e}")
            return None
    
    def synthesize(self, text, voice="aura-asteria-en"):
        try:
            print(f"🔊 Synthesizing: '{text[:50]}...' with voice {voice}")
            
            options = SpeakOptions(
                model=voice,
                encoding="linear16",
                container="wav",
                sample_rate=16000
            )
            
            response = self.client.speak.rest.v("1").stream_memory({"text": text}, options)
            audio_data = response.stream.read()
            
            print(f"✅ TTS generated: {len(audio_data)} bytes")
            return base64.b64encode(audio_data).decode("utf-8")
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return None

# ---------------- LLM Handler ---------------- #
class CerebrasHandler:
    """Handle Cerebras LLM API calls"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.cerebras.ai/v1/chat/completions"
        # Use faster model to avoid rate limits
        self.model = "llama-3.3-70b"  # Faster, less likely to hit rate limits
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
    
    def chat(self, messages, temperature=0.7, max_tokens=500, retries=3):
        import time
        
        for attempt in range(retries):
            try:
                # Rate limiting: wait if needed
                elapsed = time.time() - self.last_request_time
                if elapsed < self.min_request_interval:
                    time.sleep(self.min_request_interval - elapsed)
                
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model, 
                    "messages": messages, 
                    "temperature": temperature, 
                    "max_tokens": max_tokens
                }
                
                self.last_request_time = time.time()
                response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()['choices'][0]['message']['content']
                print(f"✅ LLM response received: {result[:50]}...")
                return result
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                    print(f"⚠️ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{retries}")
                    time.sleep(wait_time)
                else:
                    print(f"❌ LLM HTTP error: {e}")
                    if attempt == retries - 1:
                        return None
            except Exception as e:
                print(f"❌ LLM error: {e}")
                if attempt == retries - 1:
                    return None
        
        return None

# ---------------- Session ---------------- #
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
        agent_responses = []
        
        # Process agents ONE AT A TIME to avoid rate limits
        for agent in self.room['agents']:
            print(f"🤖 Processing agent: {agent.get('name', 'agent')}")
            
            messages = [{"role": "system", "content": agent['system_prompt']}]
            
            # Add recent context (last 6 messages)
            for ctx in self.context[-6:]:
                messages.append(ctx)
            
            # Add current user message
            messages.append({"role": "user", "content": user_text})
            
            # Get response from LLM
            response = llm_handler.chat(
                messages,
                temperature=agent.get('temperature', 0.7),
                max_tokens=200
            )
            
            if response:
                agent_responses.append((agent.get('name', 'agent'), response))
                print(f"✅ {agent.get('name', 'agent')}: {response[:50]}...")
            else:
                print(f"⚠️ No response from {agent.get('name', 'agent')}")
                # Use fallback response
                fallback = f"I'm {agent.get('name', 'agent')}. I'm here to help you with that."
                agent_responses.append((agent.get('name', 'agent'), fallback))

        # Update context with all responses
        final_response = " ".join([r[1] for r in agent_responses])
        self.context.extend([
            {"role": "user", "content": user_text}, 
            {"role": "assistant", "content": final_response}
        ])
        
        return agent_responses
    
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

# ---------------- Handlers ---------------- #
def initialize_handlers():
    global deepgram_client, cerebras_handler

    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    if not deepgram_key or not cerebras_key:
        raise ValueError("API keys not found in .env file")

    deepgram_client = DeepgramHandler(deepgram_key)
    cerebras_handler = CerebrasHandler(cerebras_key)
    print("✅ Core handlers initialized successfully.")

# ---------------- Routes ---------------- #
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

# ---------------- Socket.IO ---------------- #
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
        
        print(f"✅ Session started for room: {selected_room['name']}")
        
        emit('session_started', {
            'room': selected_room['name'],
            'duration': selected_room['session_duration_minutes'],
            'agents': [a['name'] for a in selected_room['agents']],
            'greeting': greeting
        })
    except Exception as e:
        print(f"❌ Session start error: {e}")
        emit('error', {'message': str(e)})

@socketio.on('process_audio')
def handle_process_audio(data):
    session = active_sessions.get(request.sid)
    if not session:
        return emit('error', {'message': 'No active session'})
    if session.is_expired():
        return emit('session_expired', {'message': 'Session time limit reached'})
    
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        audio_base64 = data.get('audio')
        if not audio_base64:
            return emit('error', {'message': 'No audio data received'})
            
        audio_file = os.path.join(temp_dir, 'input.wav')

        audio_handler = AudioHandler()
        audio_handler.save_wav_from_base64(audio_base64, audio_file)

        emit('status', {'message': 'Transcribing...', 'type': 'transcribing'})
        user_text = deepgram_client.transcribe(audio_file)
        
        if not user_text:
            return emit('error', {'message': 'Could not understand audio. Please try again.'})

        session.log_interaction('user', user_text)
        emit('transcription', {'text': user_text})

        emit('status', {'message': 'Processing...', 'type': 'processing'})
        agent_outputs = session.process_user_input(user_text, cerebras_handler)

        if not agent_outputs:
            return emit('error', {'message': 'No response from agents'})

        for agent_name, agent_text in agent_outputs:
            session.log_interaction('assistant', f"{agent_name}: {agent_text}")
            emit('agent_text', {'agent': agent_name, 'text': agent_text})

        # Voice mapping for different agents - Deepgram Aura voices
        VOICE_MAP = {
            "Coach": "aura-athena-en",      # Confident, authoritative female
            "Guide": "aura-asteria-en",     # Warm, friendly female
            "Mentor": "aura-luna-en",       # Calm, soothing female
            "Advisor": "aura-stella-en",    # Professional female
            "Expert": "aura-arcas-en",      # Deep, mature male
            "Analyst": "aura-orion-en",     # Clear, articulate male
            "Strategist": "aura-perseus-en" # Strong, confident male
        }

        # Send all agent responses with audio
        for agent_name, agent_text in agent_outputs:
            emit('status', {'message': f'{agent_name} speaking...', 'type': 'synthesizing'})
            voice_for_agent = VOICE_MAP.get(agent_name, "aura-asteria-en")
            audio_b64 = deepgram_client.synthesize(agent_text, voice=voice_for_agent)

            if audio_b64:
                emit('agent_response', {
                    'agent': agent_name,
                    'text': agent_text,
                    'audio': audio_b64,
                    'remaining_time': session.remaining_time()
                })
            else:
                print(f"⚠️ No audio generated for {agent_name}")

        emit('status', {'message': 'Ready for next question', 'type': 'done'})
        
    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        import traceback
        traceback.print_exc()
        emit('error', {'message': f'Error: {str(e)}'})
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@socketio.on('end_session')
def handle_end_session():
    session = active_sessions.get(request.sid)
    if session:
        session.save_log()
        del active_sessions[request.sid]
        print("✅ Session ended and saved")
    emit('session_ended', {'message': 'Session saved successfully'})

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_sessions:
        active_sessions[request.sid].save_log()
        del active_sessions[request.sid]
        print(f"🔌 Client disconnected: {request.sid}")

# ---------------- Main ---------------- #
if __name__ == '__main__':
    try:
        initialize_handlers()
        print("✅ AURA Backend initialized")
        print("🌐 Starting server on http://localhost:5000")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        import traceback
        traceback.print_exc()