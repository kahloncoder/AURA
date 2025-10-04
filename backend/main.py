"""
AURA - Multi-Agent Voice Assistant MVP
Main application entry point
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions
import requests
import wave
import tempfile

# Load environment variables
load_dotenv()

class ConfigLoader:
    """Load and manage rooms configuration"""
    
    @staticmethod
    def load_rooms(config_path="rooms.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def select_room(rooms):
        print("\n" + "="*60)
        print("🎭 AURA - Multi-Agent Voice Assistant")
        print("="*60)
        print("\nAvailable Scenarios:")
        
        for idx, room in enumerate(rooms['rooms'], 1):
            print(f"{idx}. {room['name']}")
            print(f"   {room['description']}")
            print(f"   Duration: {room['session_duration_minutes']} minutes")
            print()
        
        while True:
            try:
                choice = int(input("Select a scenario (number): "))
                if 1 <= choice <= len(rooms['rooms']):
                    return rooms['rooms'][choice - 1]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")


class AudioHandler:
    """Handle voice input/output"""
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = []
        self.is_recording = False
    
    def record_audio(self):
        """Record audio while user holds Enter key"""
        print("\n🎤 Press and HOLD Enter to speak, release when done...")
        input()  # Wait for Enter press
        
        print("🔴 RECORDING... (Press Enter again to stop)")
        
        self.recording = []
        self.is_recording = True
        
        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.recording.append(indata.copy())
        
        # Start recording stream
        with sd.InputStream(samplerate=self.sample_rate, channels=1, 
                           callback=callback, dtype='int16'):
            input()  # Wait for second Enter press to stop
        
        self.is_recording = False
        print("⏹️  Recording stopped\n")
        
        # Convert to numpy array
        if self.recording:
            audio_data = np.concatenate(self.recording, axis=0)
            return audio_data
        return None
    
    def save_wav(self, audio_data, filename):
        """Save audio data as WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
    
    def play_audio(self, audio_file):
        """Play audio file"""
        with wave.open(audio_file, 'rb') as wf:
            audio_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            sd.play(audio_data, wf.getframerate())
            sd.wait()


class DeepgramHandler:
    """Handle Deepgram STT and TTS"""
    
    def __init__(self, api_key):
        self.client = DeepgramClient(api_key)
    
    def transcribe(self, audio_file):
        """Convert speech to text"""
        try:
            with open(audio_file, 'rb') as f:
                buffer = f.read()
            
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                language="en"
            )
            
            response = self.client.listen.prerecorded.v('1').transcribe_file(
                {'buffer': buffer}, options
            )
            
            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            return transcript.strip()
        
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def synthesize(self, text, voice="aura-2-asteria-en", output_file="output.wav"):
        """Convert text to speech"""
        try:
            options = SpeakOptions(
                model="aura-asteria-en"
            )
            
            # Override with specific voice
            response = self.client.speak.v('1').save(
                output_file,
                {'text': text},
                options
            )
            
            return output_file
        
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return None


class CerebrasHandler:
    """Handle Cerebras LLM API calls"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.cerebras.ai/v1/chat/completions"
        self.model = "llama3.3-70b"
        self.max_tokens = 65000
    
    def chat(self, messages, temperature=0.7, max_tokens=500):
        """Make LLM API call"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
        
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return None


class SessionManager:
    """Manage conversation sessions and logging"""
    
    def __init__(self, room, duration_minutes):
        self.room_name = room['name']
        self.start_time = datetime.now()
        self.duration = timedelta(minutes=duration_minutes)
        self.end_time = self.start_time + self.duration
        self.conversation_log = []
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def is_expired(self):
        """Check if session time limit exceeded"""
        return datetime.now() >= self.end_time
    
    def remaining_time(self):
        """Get remaining session time"""
        remaining = self.end_time - datetime.now()
        return max(0, int(remaining.total_seconds()))
    
    def log_interaction(self, role, content):
        """Add interaction to log"""
        self.conversation_log.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        })
    
    def save_log(self):
        """Save conversation log to file"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir / f"aura_{self.room_name.replace(' ', '_')}_{timestamp}.json"
        
        session_data = {
            "room": self.room_name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "conversation": self.conversation_log
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Session log saved: {filename}")


class MultiAgentSystem:
    """Orchestrate multi-agent conversation flow"""
    
    def __init__(self, agents, llm_handler):
        self.agents = agents
        self.llm = llm_handler
        self.context = []
    
    def process_user_input(self, user_text):
        """Pass user input through all agents sequentially"""
        print("\n🤖 Agents processing your input...\n")
        
        agent_responses = []
        current_context = user_text
        
        for idx, agent in enumerate(self.agents, 1):
            print(f"   Agent {idx} ({agent['name']}) thinking...")
            
            # Build messages for this agent
            messages = [
                {"role": "system", "content": agent['system_prompt']}
            ]
            
            # Add conversation context
            for ctx in self.context[-6:]:  # Keep last 6 messages for context
                messages.append(ctx)
            
            # Add current input with previous agent responses
            if agent_responses:
                context_with_previous = f"User: {user_text}\n\nPrevious Agent Responses:\n"
                for i, resp in enumerate(agent_responses, 1):
                    context_with_previous += f"Agent {i}: {resp}\n"
                messages.append({"role": "user", "content": context_with_previous})
            else:
                messages.append({"role": "user", "content": current_context})
            
            # Get agent response
            response = self.llm.chat(messages, temperature=agent['temperature'], max_tokens=200)
            
            if response:
                agent_responses.append(response)
                print(f"   ✓ Agent {idx} responded\n")
            else:
                agent_responses.append("I need a moment to think about that.")
        
        # Combine all agent responses
        final_response = self._combine_responses(agent_responses)
        
        # Update context
        self.context.append({"role": "user", "content": user_text})
        self.context.append({"role": "assistant", "content": final_response})
        
        return final_response, agent_responses
    
    def _combine_responses(self, responses):
        """Combine multiple agent responses into coherent answer"""
        combined = ""
        for idx, resp in enumerate(responses, 1):
            if idx == 1:
                combined += resp
            else:
                # Add subsequent responses naturally
                combined += f" {resp}"
        return combined


def main():
    """Main application loop"""
    
    # Check for API keys
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    
    if not deepgram_key or not cerebras_key:
        print("❌ Error: API keys not found in .env file")
        print("Please create a .env file with:")
        print("DEEPGRAM_API_KEY=your_key_here")
        print("CEREBRAS_API_KEY=your_key_here")
        return
    
    # Initialize components
    config_loader = ConfigLoader()
    audio_handler = AudioHandler()
    deepgram = DeepgramHandler(deepgram_key)
    cerebras = CerebrasHandler(cerebras_key)
    
    # Load and select room
    try:
        rooms = config_loader.load_rooms()
        selected_room = config_loader.select_room(rooms)
    except FileNotFoundError:
        print("❌ Error: rooms.json not found")
        return
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # Initialize session
    session = SessionManager(selected_room, selected_room['session_duration_minutes'])
    
    # Initialize multi-agent system
    multi_agent = MultiAgentSystem(selected_room['agents'], cerebras)
    
    print(f"\n✅ Session started: {selected_room['name']}")
    print(f"⏱️  Duration: {selected_room['session_duration_minutes']} minutes")
    print(f"🤖 Agents: {', '.join([a['name'] for a in selected_room['agents']])}")
    print("\n" + "="*60)
    
    # Initial greeting
    greeting = selected_room.get('greeting', 'Hello! How can I help you today?')
    print(f"\n🤖 AURA: {greeting}\n")
    session.log_interaction("assistant", greeting)
    
    # Main conversation loop
    temp_dir = tempfile.mkdtemp()
    
    try:
        while not session.is_expired():
            # Show remaining time
            remaining = session.remaining_time()
            print(f"⏱️  Time remaining: {remaining // 60}m {remaining % 60}s")
            
            # Record user input
            audio_data = audio_handler.record_audio()
            
            if audio_data is None or len(audio_data) == 0:
                print("⚠️  No audio recorded. Please try again.")
                continue
            
            # Save and transcribe
            audio_file = os.path.join(temp_dir, "user_input.wav")
            audio_handler.save_wav(audio_data, audio_file)
            
            print("🔄 Transcribing...")
            user_text = deepgram.transcribe(audio_file)
            
            if not user_text:
                print("⚠️  Could not understand. Please try again.")
                continue
            
            print(f"\n👤 You: {user_text}")
            session.log_interaction("user", user_text)
            
            # Check for exit commands
            if user_text.lower() in ['exit', 'quit', 'goodbye', 'bye']:
                farewell = "Goodbye! Thank you for using AURA."
                print(f"\n🤖 AURA: {farewell}")
                session.log_interaction("assistant", farewell)
                break
            
            # Process through agents
            response, agent_responses = multi_agent.process_user_input(user_text)
            
            print(f"\n🤖 AURA: {response}\n")
            session.log_interaction("assistant", response)
            
            # Synthesize and play response
            print("🔊 Speaking...")
            tts_file = os.path.join(temp_dir, "response.wav")
            if deepgram.synthesize(response, output_file=tts_file):
                audio_handler.play_audio(tts_file)
            
            print("\n" + "-"*60 + "\n")
        
        if session.is_expired():
            print("\n⏰ Session time limit reached.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted by user.")
    
    finally:
        # Save session log
        session.save_log()
        print("\n✅ AURA session ended. Goodbye!\n")
        
        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()