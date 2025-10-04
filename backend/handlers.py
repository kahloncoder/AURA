"""
AURA Handlers
Audio processing, Speech-to-Text, Text-to-Speech, and LLM interactions
"""

import os
import base64
import time
import subprocess
import requests
from deepgram import DeepgramClient # Reverted to the correct import for the older SDK
from config import *


# ============================================================================
# AUDIO HANDLER
# ============================================================================

class AudioHandler:
    """Handles audio format conversion using ffmpeg"""
    
    @staticmethod
    def save_wav_from_base64(audio_base64, filename):
        """
        Convert base64-encoded WebM/OGG audio to 16kHz mono WAV using ffmpeg
        """
        try:
            audio_bytes = base64.b64decode(audio_base64)
            tmp_in = filename + ".tmp"

            with open(tmp_in, "wb") as f:
                f.write(audio_bytes)

            def run_ffmpeg(input_format=None):
                cmd = [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error"
                ]
                if input_format:
                    cmd += ["-f", input_format]
                cmd += [
                    "-i", tmp_in,
                    "-ac", "1",
                    "-ar", str(SAMPLE_RATE),
                    "-sample_fmt", "s16",
                    "-f", "wav",
                    filename
                ]
                return subprocess.run(cmd, capture_output=True)

            result = run_ffmpeg("webm")
            if result.returncode != 0:
                print("⚠️ WebM decode failed, trying OGG...")
                result = run_ffmpeg("ogg")

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr.decode()}")

            with open(filename, "rb") as f:
                out_bytes = f.read()

            print(f"✅ Audio converted to WAV: {len(out_bytes)} bytes")
            return out_bytes

        except Exception as e:
            print(f"❌ Audio conversion error: {e}")
            return None
        finally:
            try:
                os.remove(tmp_in)
            except:
                pass


# ============================================================================
# DEEPGRAM HANDLER (Reverted to be compatible with deepgram-sdk==3.5.0)
# ============================================================================

class DeepgramHandler:
    """Handles Deepgram API for STT and TTS"""
    
    def __init__(self, api_key):
        self.client = DeepgramClient(api_key)
    
    def transcribe(self, audio_file):
        """
        Convert speech to text
        """
        try:
            with open(audio_file, 'rb') as f:
                buffer = f.read()
            
            print(f"🎤 Transcribing {len(buffer)} bytes...")
            
            # Using a dictionary for options, compatible with the older SDK
            options = {
                "smart_format": True,
                "model": "nova-2",
                "language": "en"
            }

            response = self.client.listen.prerecorded.v("1").transcribe_file(
                {'buffer': buffer}, options
            )
            
            # Accessing the response as a dictionary
            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            if transcript:
                print(f"✅ Transcription: {transcript}")
                return transcript.strip()
            
            print("⚠️ No transcription returned")
            return None
        
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def synthesize(self, text, voice):
        """
        Convert text to speech
        """
        try:
            print(f"🔊 Synthesizing with {voice}: '{text[:50]}...'")
            
            options = {
                "model": voice,
                "encoding": AUDIO_FORMAT,
                "container": AUDIO_CONTAINER,
                "sample_rate": SAMPLE_RATE
            }
            
            response = self.client.speak.v("1").stream(
                {"text": text}, options
            )
            
            # --- FIX IS HERE: Changed response.get('stream') to response.stream ---
            audio_data = response.stream.read()
            
            print(f"✅ TTS generated: {len(audio_data)} bytes")
            return base64.b64encode(audio_data).decode("utf-8")
            
        except Exception as e:
            print(f"❌ TTS error for voice '{voice}': {e}")
            return None


# ============================================================================
# CEREBRAS HANDLER
# ============================================================================

class CerebrasHandler:
    """Handles Cerebras LLM API with rate limiting"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.last_request_time = 0
    
    def chat(self, messages):
        """
        Get LLM response with automatic retry
        """
        for attempt in range(MAX_RETRIES):
            try:
                elapsed = time.time() - self.last_request_time
                if elapsed < MIN_REQUEST_INTERVAL:
                    time.sleep(MIN_REQUEST_INTERVAL - elapsed)
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": CEREBRAS_MODEL,
                    "messages": messages,
                    "max_tokens": MAX_TOKENS
                }
                
                self.last_request_time = time.time()
                response = requests.post(
                    CEREBRAS_BASE_URL,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()['choices'][0]['message']['content']
                print(f"✅ LLM response: {result[:50]}...")
                return result
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = (attempt + 1) * 2
                    print(f"⚠️ Rate limited. Waiting {wait_time}s (retry {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(wait_time)
                else:
                    print(f"❌ LLM HTTP error: {e}")
                    if attempt == MAX_RETRIES - 1:
                        return None
            except Exception as e:
                print(f"❌ LLM error: {e}")
                if attempt == MAX_RETRIES - 1:
                    return None
        
        return None


# ============================================================================
# INITIALIZE GLOBAL HANDLERS
# ============================================================================

def initialize_handlers():
    """Initialize all handlers"""
    global deepgram_client, cerebras_handler
    
    deepgram_client = DeepgramHandler(DEEPGRAM_API_KEY)
    cerebras_handler = CerebrasHandler(CEREBRAS_API_KEY)
    
    print("✅ All handlers initialized")

# Initialize handlers when module is imported
deepgram_client = None
cerebras_handler = None
initialize_handlers()