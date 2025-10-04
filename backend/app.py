"""
AURA - Multi-Agent Voice Assistant
Main Flask application with modular structure
"""

import json
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

# Import configurations and modules
from config import *
from handlers import initialize_handlers, deepgram_client, cerebras_handler
from socket_events import register_socket_events

# Initialize handlers before creating socket events
initialize_handlers()


# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading'
)


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    return {"message": "AURA Backend running!"}

    """Serve main web interface"""
    # return render_template('index.html')


@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all available conversation rooms"""
    try:
        with open(ROOMS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            rooms_data = json.load(f)
        
        # Validate voice assignments
        for room in rooms_data.get('rooms', []):
            for idx, agent in enumerate(room.get('agents', [])):
                voice = agent.get('voice', '')
                if not voice or not voice.startswith('aura-'):
                    agent['voice'] = DEFAULT_VOICES[idx % len(DEFAULT_VOICES)]
        
        return jsonify(rooms_data)
    
    except Exception as e:
        print(f"❌ Error loading rooms: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/custom-room', methods=['POST'])
def create_custom_room():
    """
    Create custom room with user-defined agents
    
    Expected JSON:
    {
        "agents": [
            {"name": "Agent1", "prompt": "...", "voice": "aura-asteria-en"},
            {"name": "Agent2", "prompt": "..."},
            {"name": "Agent3", "prompt": "..."}
        ],
        "duration_minutes": 5 or 15
    }
    """
    try:
        data = request.json
        agents_data = data.get('agents', [])
        duration = data.get('duration_minutes', 5)
        
        # Validate
        if len(agents_data) != 3:
            return jsonify({"error": "Exactly 3 agents required"}), 400
        
        if duration not in ALLOWED_DURATIONS:
            return jsonify({
                "error": f"Duration must be {' or '.join(map(str, ALLOWED_DURATIONS))} minutes"
            }), 400
        
        # Build custom room
        custom_room = {
            "name": "Custom Session",
            "description": "Your personalized AI conversation",
            "session_duration_minutes": duration,
            "greeting": "Welcome! Your three personalized agents are ready.",
            "agents": []
        }
        
        for idx, agent in enumerate(agents_data):
            custom_room["agents"].append({
                "name": agent.get('name', f'Agent {idx + 1}').strip(),
                "role": "custom",
                "personality": "custom",
                "system_prompt": agent.get('prompt', f'You are Agent {idx + 1}. Provide helpful, concise responses under 50 words.'),
                "voice": agent.get('voice', DEFAULT_VOICES[idx])
            })
        
        return jsonify({"room": custom_room, "success": True})
    
    except Exception as e:
        print(f"❌ Error creating custom room: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("🎭 AURA - Multi-Agent Voice Assistant")
        print("="*60)
        
        # Validate configuration
        validate_config()
        
        # Initialize handlers
        initialize_handlers()
        
        # Register SocketIO events
        register_socket_events(socketio)
        
        # MongoDB initialization (for future use)
        # from database import initialize_mongodb
        # initialize_mongodb()
        
        print("✅ All systems initialized")
        print("🌐 Server: http://0.0.0.0:5000")
        print("="*60 + "\n")
        
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=5000,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        print(f"\n❌ Startup Error: {e}")
        import traceback
        traceback.print_exc()