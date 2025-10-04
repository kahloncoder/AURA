# 🔗 AURA Frontend-Backend Connection Guide

## 📁 Project Structure

```
aura-project/
│
├── backend/                      # Flask Backend
│   ├── app.py                    # Main Flask app
│   ├── config.py                 # Configuration
│   ├── handlers.py               # Audio, STT, TTS, LLM handlers
│   ├── session.py                # Session management
│   ├── socket_events.py          # SocketIO events
│   ├── database.py               # MongoDB (future)
│   ├── rooms.json                # Room configurations
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # API keys
│   └── logs/                     # Session logs (auto-created)
│
└── frontend/                     # React Frontend (Lovable project)
    ├── src/
    │   ├── components/           # UI components
    │   ├── pages/                # Page components
    │   ├── services/             # API & Socket services
    │   ├── hooks/                # Custom React hooks
    │   └── lib/                  # Utilities
    ├── public/
    └── package.json
```

## 🚀 Step-by-Step Setup

### 1. Backend Setup

#### A. Create Backend Folder
```bash
# Create backend directory outside the Lovable project
mkdir aura-project
cd aura-project
mkdir backend
cd backend
```

#### B. Copy Backend Files
Copy these files from your uploads to the `backend/` folder:
- `app.py`
- `config.py`
- `handlers.py`
- `session.py`
- `socket_events.py`
- `database.py`
- `rooms.json`
- `requirements.txt`

#### C. Create `.env` File
```bash
# Create .env in backend folder
cat > .env << EOF
DEEPGRAM_API_KEY=your_deepgram_key_here
CEREBRAS_API_KEY=your_cerebras_key_here
FLASK_SECRET_KEY=your_random_secret_key_here
EOF
```

#### D. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# If you don't have requirements.txt, install manually:
pip install flask flask-socketio flask-cors python-dotenv deepgram-sdk requests
```

#### E. Start Backend Server
```bash
python app.py
```

Server will start at: `http://localhost:5000`

---

### 2. Frontend Setup

#### A. Your Lovable project is already set up!
The frontend code is already in your Lovable project.

#### B. Install Socket.IO Client
Already done! `socket.io-client` is installed.

#### C. Configure Backend URL
The frontend will connect to: `http://localhost:5000`

---

### 3. Running Both Servers

#### Terminal 1 - Backend
```bash
cd aura-project/backend
python app.py
```
✅ Backend running on `http://localhost:5000`

#### Terminal 2 - Frontend
Your Lovable project automatically runs the frontend.
✅ Frontend running on Lovable's preview

---

## 🌐 Connecting Frontend to Backend

### Option 1: Local Development (Current Setup)

**Backend URL**: `http://localhost:5000`

The frontend code will automatically connect when both servers are running.

### Option 2: Backend on Same Domain (Production)

If you deploy both together:
```typescript
// In socketService.ts, use relative URL
const SOCKET_URL = window.location.origin;
```

### Option 3: Backend on Different Server

```typescript
// In socketService.ts
const SOCKET_URL = 'https://your-backend-domain.com';
```

---

## 🗄️ MongoDB Setup (Optional - For Later)

Currently, conversations are saved to `backend/logs/` as JSON files.

### To Enable MongoDB:

1. Install MongoDB locally or use MongoDB Atlas (cloud)

2. Update `.env`:
```bash
MONGO_URI=mongodb://localhost:27017/
# OR for MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/aura
```

3. Uncomment MongoDB code in:
   - `config.py` (lines 65-66)
   - `session.py` (all commented sections)
   - `app.py` (lines 140-141)

4. Install PyMongo:
```bash
pip install pymongo
```

---

## 🔒 CORS Configuration

The backend is configured to accept connections from any origin:
```python
# In app.py
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
```

For production, restrict CORS:
```python
# Only allow your frontend domain
CORS(app, origins=["https://your-frontend-domain.com"])
socketio = SocketIO(
    app, 
    cors_allowed_origins=["https://your-frontend-domain.com"]
)
```

---

## 🧪 Testing the Connection

### 1. Test Backend API
```bash
# Get available rooms
curl http://localhost:5000/api/rooms
```

### 2. Test Frontend Connection
1. Open your Lovable preview
2. Go to `/dashboard`
3. Click "Start Session" on any room
4. Check browser console for connection logs

---

## 📡 WebSocket Events

### Frontend → Backend

| Event | Data | Description |
|-------|------|-------------|
| `start_session` | `{ room: {...} }` | Initialize session |
| `process_audio` | `{ audio: base64 }` | Send audio for processing |
| `end_session` | - | End current session |

### Backend → Frontend

| Event | Data | Description |
|-------|------|-------------|
| `session_started` | Session info | Session initialized |
| `transcription` | `{ text: string }` | User speech transcribed |
| `agent_status` | Agent status | Agent thinking/speaking |
| `agent_response` | Agent response + audio | Agent's response ready |
| `processing_complete` | Summary | All agents finished |
| `session_ended` | Message | Session saved |
| `error` | Error info | Error occurred |

---

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check if port 5000 is already in use
lsof -i :5000
# Kill existing process if needed
kill -9 <PID>
```

### Frontend Can't Connect
1. Check backend is running: `curl http://localhost:5000/api/rooms`
2. Check browser console for errors
3. Verify CORS is enabled in backend
4. Try restarting both servers

### Audio Not Working
1. Check microphone permissions in browser
2. Verify Deepgram API key is valid
3. Check browser console for audio errors
4. Ensure HTTPS is used (required for microphone access)

### MongoDB Connection Issues
1. Check MongoDB is running: `mongosh`
2. Verify connection string in `.env`
3. Check network access (especially for MongoDB Atlas)

---

## 📦 Deployment Options

### Option 1: Separate Deployment

**Backend**: Deploy to Heroku, Railway, DigitalOcean, AWS
**Frontend**: Lovable handles deployment automatically

### Option 2: Same Server

Use a reverse proxy (nginx) to serve both:
```nginx
# Frontend
location / {
    proxy_pass http://localhost:3000;
}

# Backend API
location /api {
    proxy_pass http://localhost:5000;
}

# WebSocket
location /socket.io {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 🔐 Security Checklist

- [ ] Use strong `FLASK_SECRET_KEY` in production
- [ ] Restrict CORS origins in production
- [ ] Use HTTPS for all connections
- [ ] Store API keys in environment variables (never in code)
- [ ] Add rate limiting to API endpoints
- [ ] Validate all user inputs
- [ ] Implement authentication (if needed)
- [ ] Secure MongoDB with authentication

---

## 📊 Monitoring & Logs

### Backend Logs
Located in `backend/logs/`
- Session JSON files with full conversation history
- Filenames: `aura_RoomName_YYYYMMDD_HHMMSS.json`

### Frontend Logs
- Browser console (development)
- Add error tracking (Sentry, LogRocket) for production

---

## 🎯 Next Steps

1. ✅ Set up backend folder structure
2. ✅ Install dependencies
3. ✅ Configure API keys
4. ✅ Start both servers
5. ✅ Test connection
6. 🔄 Add MongoDB (optional)
7. 🚀 Deploy to production

---

**Need Help?** Check the console logs in both backend terminal and browser console for detailed error messages.
