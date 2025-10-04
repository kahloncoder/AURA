"""
AURA SocketIO Event Handlers
Real-time communication between frontend and backend
"""

import os
import json
import tempfile
import shutil
from flask import request
from flask_socketio import emit
from session import SessionManager
from handlers import AudioHandler, deepgram_client, cerebras_handler, initialize_handlers

# Ensure handlers are initialized
initialize_handlers()


# ============================================================================
# ACTIVE SESSIONS STORE
# ============================================================================

active_sessions = {}


# ============================================================================
# SOCKET EVENT HANDLERS
# ============================================================================

def register_socket_events(socketio):
    """Register all SocketIO event handlers"""
    
    @socketio.on('start_session')
    def handle_start_session(data):
        """Initialize new conversation session"""
        try:
            room_data = data.get('room')
            
            if not room_data:
                # Load from rooms.json
                with open('rooms.json', 'r', encoding='utf-8') as f:
                    rooms = json.load(f)
                room_index = data.get('room_index', 0)
                selected_room = rooms['rooms'][room_index]
            else:
                # Custom room provided
                selected_room = room_data
            
            # Create session
            session = SessionManager(
                selected_room,
                selected_room['session_duration_minutes']
            )
            active_sessions[request.sid] = session
            
            # Log greeting
            greeting = selected_room.get('greeting', 'Hello! How can I help?')
            session.log_interaction('assistant', greeting)
            
            print(f"✅ Session started: {selected_room['name']} ({request.sid})")
            
            emit('session_started', {
                'room': selected_room['name'],
                'duration': selected_room['session_duration_minutes'],
                'agents': [
                    {
                        'name': a['name'],
                        'voice': session.get_voice_for_agent(a, idx)
                    }
                    for idx, a in enumerate(selected_room['agents'])
                ],
                'greeting': greeting
            })
            
        except Exception as e:
            print(f"❌ Session start error: {e}")
            import traceback
            traceback.print_exc()
            emit('error', {'message': str(e), 'recoverable': False})
    
    
    @socketio.on('process_audio')
    def handle_process_audio(data):
        """
        Process user audio with PSEUDO-STREAMING
        Each agent response is sent immediately after generation
        """
        session = active_sessions.get(request.sid)
        
        if not session:
            return emit('error', {
                'message': 'No active session',
                'recoverable': False
            })
        
        if session.is_expired():
            return emit('session_expired', {
                'message': 'Session time limit reached',
                'recoverable': False
            })
        
        temp_dir = None
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            
            audio_base64 = data.get('audio')
            if not audio_base64:
                return emit('error', {
                    'message': 'No audio data received',
                    'recoverable': True
                })
            
            # Convert audio
            audio_file = os.path.join(temp_dir, 'input.wav')
            AudioHandler.save_wav_from_base64(audio_base64, audio_file)
            
            # Transcribe
            emit('status', {'message': 'Listening...', 'type': 'transcribing'})
            user_text = deepgram_client.transcribe(audio_file)
            
            if not user_text:
                return emit('error', {
                    'message': 'Could not understand. Please try again.',
                    'recoverable': True
                })
            
            # Log and send transcription
            session.log_interaction('user', user_text)
            emit('transcription', {'text': user_text})
            
            # Process through agents with STREAMING
            emit('status', {'message': 'Processing...', 'type': 'processing'})
            
            agent_responses = session.process_agents_streaming(
                user_text,
                cerebras_handler,
                deepgram_client,
                emit  # Pass emit for streaming
            )
            
            # All done
            emit('status', {
                'message': 'Ready for next question',
                'type': 'complete'
            })
            
            emit('processing_complete', {
                'total_agents': len(agent_responses),
                'remaining_time': session.remaining_time()
            })
            
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            import traceback
            traceback.print_exc()
            emit('error', {
                'message': f'Error: {str(e)}',
                'recoverable': True
            })
        
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    
    @socketio.on('end_session')
    def handle_end_session():
        """End session and save logs"""
        session = active_sessions.get(request.sid)
        
        if session:
            session.save_log()
            del active_sessions[request.sid]
            print(f"✅ Session ended: {request.sid}")
        
        emit('session_ended', {'message': 'Session saved'})
    
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        if request.sid in active_sessions:
            active_sessions[request.sid].save_log()
            del active_sessions[request.sid]
            print(f"🔌 Disconnected: {request.sid}")