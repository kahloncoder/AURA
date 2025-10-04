"""
AURA - Multi-Agent Voice Assistant
Main Flask application with modular structure
"""

import json
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from bson import ObjectId # <-- ADDED: Needed to handle MongoDB IDs

# Import configurations and modules
from config import *
from handlers import initialize_handlers, deepgram_client, cerebras_handler
from socket_events import register_socket_events
from database import db 

import jwt
from datetime import datetime, timedelta, timezone
from user_model import create_user, check_password


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


@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all available conversation rooms"""
    try:
        with open(ROOMS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            rooms_data = json.load(f)
        
        for room in rooms_data.get('rooms', []):
            for idx, agent in enumerate(room.get('agents', [])):
                voice = agent.get('voice', '')
                if not voice or not voice.startswith('aura-'):
                    agent['voice'] = DEFAULT_VOICES[idx % len(DEFAULT_VOICES)]
        
        return jsonify(rooms_data)
    
    except Exception as e:
        print(f"❌ Error loading rooms: {e}")
        return jsonify({"error": str(e)}), 500
    
# ============================================================================
# ---   AUTHENTICATION ROUTES ---
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user_id = create_user(email, password)
        return jsonify({"message": "User created successfully", "userId": str(user_id)}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # 409 Conflict for existing user
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = db.users.find_one({"email": email})

        if not user or not check_password(user['password'], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Create the token
        payload = {
            'sub': str(user['_id']), # Subject (the user's ID)
            'iat': datetime.now(timezone.utc), # Issued at
            'exp': datetime.now(timezone.utc) + timedelta(days=7) # Expiration
        }
        
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": { "id": str(user['_id']), "email": user['email'] }
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# ============================================================================

# ============================================================================
# --- NEW: API ENDPOINTS FOR MONGODB CONVERSATIONS ---
# ============================================================================

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get a list of recent conversation summaries"""
    if db is None:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        sessions_cursor = db.sessions.find(
            {"status": "completed"},
            {"conversation": 0}
        ).sort("start_time", -1).limit(50)
        
        sessions = []
        for session in sessions_cursor:
            session['_id'] = str(session['_id'])
            sessions.append(session)
            
        return jsonify(sessions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversations/<session_id>', methods=['GET'])
def get_conversation_details(session_id):
    """Get the full details of a single conversation"""
    if db is None:
        return jsonify({"error": "Database not connected"}), 500
        
    try:
        session = db.sessions.find_one({"_id": ObjectId(session_id)})
        if session:
            session['_id'] = str(session['_id'])
            return jsonify(session)
        return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================

@app.route('/api/custom-room', methods=['POST'])
def create_custom_room():
    """Create custom room with user-defined agents"""
    try:
        data = request.json
        agents_data = data.get('agents', [])
        duration = data.get('duration_minutes', 5)
        
        if len(agents_data) != 3:
            return jsonify({"error": "Exactly 3 agents required"}), 400
        
        if duration not in ALLOWED_DURATIONS:
            return jsonify({
                "error": f"Duration must be {' or '.join(map(str, ALLOWED_DURATIONS))} minutes"
            }), 400
        
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
                "system_prompt": agent.get('prompt', f'You are Agent {idx + 1}.'),
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
        
        validate_config()
        initialize_handlers()
        register_socket_events(socketio)
        
        # --- MODIFIED: MongoDB is now initialized on startup ---
        from database import initialize_mongodb
        initialize_mongodb()
        
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