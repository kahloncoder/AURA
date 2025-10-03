# 🎭 AURA - Multi-Agent Voice Assistant

A sophisticated console-based voice assistant that uses multiple AI agents with different personalities to provide comprehensive, multi-perspective responses to your questions.

## 🌟 Features

- **Multi-Agent Architecture**: 3 specialized agents per scenario, each with unique personalities
- **Voice Interface**: Natural voice input/output using Deepgram
- **Configurable Scenarios**: Easy-to-customize rooms for different use cases
- **Session Management**: Timed sessions with automatic conversation logging
- **Context-Aware**: Maintains conversation context up to 65k tokens
- **Sequential Processing**: User input flows through all agents for comprehensive responses

## 🏗️ Architecture

```
User Input (Voice)
    ↓
Speech-to-Text (Deepgram)
    ↓
Agent 1 (Processes & Responds)
    ↓
Agent 2 (Processes User + Agent 1)
    ↓
Agent 3 (Processes User + Agent 1 + Agent 2)
    ↓
Combined Response
    ↓
Text-to-Speech (Deepgram)
    ↓
Audio Output
```

## 📋 Prerequisites

- Python 3.11 or higher
- Microphone for voice input
- Speakers/headphones for audio output
- API Keys:
  - [Deepgram API Key](https://console.deepgram.com/)
  - [Cerebras Cloud API Key](https://cloud.cerebras.ai/)

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
# Create project directory
mkdir aura-assistant
cd aura-assistant
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# DEEPGRAM_API_KEY=your_actual_key_here
# CEREBRAS_API_KEY=your_actual_key_here
```

### 4. Run AURA

```bash
python main.py
```

## 🎮 How to Use

1. **Select a Scenario**: Choose from available rooms (Business, Career, Technical, etc.)
2. **Voice Input**: 
   - Press and HOLD Enter to start recording
   - Speak your question
   - Press Enter again to stop recording
3. **Agent Processing**: Watch as 3 agents process your input sequentially
4. **Hear Response**: AURA speaks the combined response
5. **Continue Conversation**: Repeat until session ends or you say "exit"

### Voice Commands

- `exit`, `quit`, `goodbye`, `bye` - End the session

## 📁 Project Structure

```
aura-assistant/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── .env                # API keys (create from .env.example)
├── .env.example        # Environment template
├── rooms.json          # Agent configurations
├── logs/               # Session logs (auto-created)
│   └── aura_*.json    # Individual session files
└── README.md          # This file
```

## ⚙️ Configuration

### rooms.json Structure

Each room defines a conversation scenario:

```json
{
  "name": "Scenario Name",
  "description": "What this scenario is for",
  "session_duration_minutes": 5,
  "greeting": "Initial message to user",
  "agents": [
    {
      "name": "Agent Name",
      "role": "agent_function",
      "personality": "personality_type",
      "system_prompt": "Detailed instructions for this agent",
      "temperature": 0.5,
      "voice": "aura-voice-name"
    }
  ]
}
```

### Adding New Scenarios

1. Open `rooms.json`
2. Copy an existing room structure
3. Modify agent personalities and prompts
4. Save and restart AURA

### Agent Personality Types

- **analytical_direct**: Data-driven, no nonsense
- **bold_provocative**: Challenges assumptions
- **practical_friendly**: Warm but realistic
- **wise_straightforward**: Experience-based advice
- **blunt_factual**: Raw truth, no sugar coating
- **chaotic_creative**: Wild, unconventional ideas
- **empathetic_gentle**: Understanding and supportive

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY rooms.json .

# Create logs directory
RUN mkdir -p logs

# Run the application
CMD ["python", "main.py"]
EOF

# Build image
docker build -t aura-assistant .
```

### Run with Docker

```bash
# Run container with environment variables
docker run -it --rm \
  --device /dev/snd \
  -e DEEPGRAM_API_KEY=your_key \
  -e CEREBRAS_API_KEY=your_key \
  -v $(pwd)/logs:/app/logs \
  aura-assistant
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  aura:
    build: .
    stdin_open: true
    tty: true
    devices:
      - /dev/snd:/dev/snd
    environment:
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      - CEREBRAS_API_KEY=${CEREBRAS_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./rooms.json:/app/rooms.json
```

Run with: `docker-compose up`

## 📊 Session Logs

Every conversation is automatically saved to `logs/` directory:

```json
{
  "room": "Business Strategy Discussion",
  "start_time": "2025-10-03T10:30:00",
  "end_time": "2025-10-03T10:35:00",
  "duration_seconds": 300,
  "conversation": [
    {
      "timestamp": "2025-10-03T10:30:15",
      "role": "user",
      "content": "Should we expand to new markets?"
    },
    {
      "timestamp": "2025-10-03T10:30:25",
      "role": "assistant",
      "content": "Combined agent response..."
    }
  ]
}
```

## 🔧 Troubleshooting

### Audio Issues

```bash
# Test microphone
python -c "import sounddevice as sd; print(sd.query_devices())"

# If no devices found, check system audio settings
```

### API Errors

- **Deepgram**: Verify API key at https://console.deepgram.com/
- **Cerebras**: Check quota at https://cloud.cerebras.ai/

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## 🎯 Customization Tips

### Adjust Agent Responses

- **Shorter responses**: Reduce `max_tokens` in code (currently 200)
- **More creative**: Increase `temperature` (0.0-1.0)
- **More focused**: Decrease `temperature`

### Change Session Duration

Edit `session_duration_minutes` in rooms.json:
- Default: 5 minutes
- Extended: 15 minutes
- Custom: Any value in minutes

### Modify Context Window

In `main.py`, adjust context retention:
```python
# Keep last N messages (currently 6)
for ctx in self.context[-6:]:
```

## 🔒 Security Notes

- **Never commit `.env`** to version control
- Keep API keys secure
- Logs may contain sensitive conversation data
- Review logs before sharing

## 📝 Best Practices

1. **Clear Questions**: Ask specific, focused questions
2. **Natural Speech**: Speak naturally, don't rush
3. **Wait for Processing**: Let all agents complete before next input
4. **Review Logs**: Check saved conversations for insights
5. **Experiment with Rooms**: Try different scenarios for different needs

## 🚧 Limitations

- **Context Limit**: 65k tokens (~50k words)
- **Session Time**: Max 15 minutes per session
- **Sequential Processing**: Agents process one at a time
- **Voice Only**: No visual interface
- **English Only**: Currently configured for English

## 🔮 Future Enhancements

- [ ] Real-time interruption support
- [ ] Multi-language support
- [ ] Visual dashboard
- [ ] Agent personality customization UI
- [ ] Cloud deployment templates
- [ ] Mobile app integration
- [ ] Conversation analytics

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration in `rooms.json`
3. Verify API keys in `.env`
4. Test audio devices

## 🎉 Credits

Built with:
- **Deepgram** - Speech-to-Text & Text-to-Speech
- **Cerebras Cloud** - Llama 3.3 70B LLM
- **Python** - Core programming language

---

**Made with ❤️ for conversational AI**
