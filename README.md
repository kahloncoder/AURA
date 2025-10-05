# 🎭 AURA: Multi-Agent Voice Assistant for Collective Intelligence

> **Live Demo:** [🌐 aura.kahlonai.com](https://aura.kahlonai.com)  
> **Built for FutureStack GenAI Hackathon** — powered by **Cerebras**, **Meta Llama**, and **Docker**

---

## 🧠 Overview

**AURA** is an AI-powered **multi-agent voice assistant** that simulates collaborative human reasoning — three distinct AI personas debate, refine, and combine their perspectives to deliver the most balanced and insightful answer possible.

It's not just a voice assistant — it's a **panel of AI experts** who think together.

Built using:
- **Cerebras Cloud API** for ultra-fast inference with **Llama 3.3 (70B)**
- **Deepgram** for real-time voice input/output
- **Flask + React + Socket.IO** for seamless real-time communication
- **Docker Compose** for one-command deployment across backend, frontend, and MongoDB

---

## 🚀 Why AURA?

Modern AI assistants often mimic a single personality — logical, empathetic, or creative — but never *all three*.  
AURA bridges that gap with **multi-agent orchestration**, giving users:
- Multiple viewpoints instead of a single static answer  
- Collaborative reasoning between specialized agents  
- Immersive voice-based interactions  
- Persistent context awareness & session memory  

This makes AURA ideal for:
- Brainstorming new ideas  
- Strategy & business discussions  
- Emotional and empathetic support scenarios  
- Educational simulations  

---

## 🌍 Tech Stack

| Layer | Technology | Description |
|-------|-------------|-------------|
| 🧠 LLM | **Cerebras Cloud (Llama 3.3 70B)** | Core intelligence for all agents |
| 🔊 Speech | **Deepgram STT + TTS** | Real-time voice transcription & synthesis |
| ⚙️ Backend | **Flask + Socket.IO** | Orchestrates agent pipeline & sessions |
| 💻 Frontend | **React** | Interactive dashboard for voice sessions |
| 🐋 Deployment | **Docker Compose** | Scalable multi-service setup |
| 🗄️ Database | **MongoDB (optional)** | Persistent storage for conversations |

---

## ⚡ Hackathon Relevance

| Sponsor | Integration | Hack Value |
|----------|--------------|-------------|
| **Cerebras** 🧠 | Used for fast, large-context inference (Llama 3.3 70B) with multi-agent chaining | Demonstrates advanced prompt routing and conversational reasoning |
| **Meta** 💬 | Leverages open-source **Llama models** for personality-driven agents | Showcases generative dialogue diversity |
| **Docker** 🐋 | Full **Docker Compose** setup (frontend + backend + MongoDB) | Enables reproducible, cloud-native deployment in one command |

---

## 💡 Core Innovation

### 🎙️ Multi-Agent Architecture

AURA features **three distinct agents** per session, each with its own personality and reasoning pattern.

```
User (Voice Input)
        ↓
  Deepgram STT
        ↓
Agent 1 → Agent 2 → Agent 3 (Cerebras API)
        ↓
Consensus Generation
        ↓
Deepgram TTS (Voice Output)
```

Each agent builds on the last, providing a **multi-perspective synthesis** of logic, emotion, and creativity.

---

### 🧩 Architecture Diagram

```
            ┌──────────────────────────┐
            │        Frontend          │
            │ (React + Socket.IO UI)   │
            └────────────┬─────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │     Flask API    │
              │ SocketIO Server  │
              └───────┬──────────┘
                      │
         ┌────────────┴─────────────┐
         │  Audio + STT (Deepgram)  │
         │  LLM Agents (Cerebras)   │
         │  Session Logging (JSON)  │
         └────────────┬─────────────┘
                      │
                      ▼
                 MongoDB (optional)
```

---

## 🧰 Features

- 🎙 **Voice-driven interaction** (no typing needed)
- 🧩 **3-Agent reasoning** (logic + emotion + creativity)
- 🧠 **Context retention** for multi-turn dialogue
- 🕒 **Timed sessions** with automatic logging
- 🗃 **Session logs saved as JSON**
- 🧍‍♂️ **Personality profiles** for agents (editable in `rooms.json`)
- 🐳 **One-command Docker setup**

---

## 🛠 Setup Guide

### 🔧 Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- API Keys:
  - [Deepgram](https://console.deepgram.com/)
  - [Cerebras Cloud](https://cloud.cerebras.ai/)

---

### 🐳 Quick Start (Docker Compose)

```bash
# Clone the repo
git clone https://github.com/yourusername/aura.git
cd aura

# Start all services (frontend, backend, mongo)
docker-compose up --build
```

✅ **Backend** → http://localhost:5000  
✅ **Frontend** → http://localhost:3000  
✅ **Live Demo** → [aura.kahlonai.com](https://aura.kahlonai.com)

---

### 🧩 Docker Compose Configuration

```yaml
services:
  backend:
    build: ./backend
    ports: ["5000:5000"]
    env_file: ./backend/.env
    depends_on: [mongo]
    restart: always

  frontend:
    build: ./frontend
    ports: ["3000:8080"]
    depends_on: [backend]
    restart: always

  mongo:
    image: mongo:latest
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```

---

## 🎮 How It Works

1. 🎤 **User speaks a query**
2. 🧏 **Deepgram converts it to text**
3. 🧠 **Agent 1 (Analytical) responds**
4. 💬 **Agent 2 (Empathetic) refines**
5. 💡 **Agent 3 (Creative) finalizes the collective response**
6. 🔊 **AURA speaks the final answer**

Each session log is auto-saved under `/backend/logs/`.

---

## 🎨 UX & Design

- Modern minimal UI built in React
- Real-time transcription view
- Visual agent status indicators (Thinking → Speaking → Complete)
- Session summary at end
- Dark/light theme ready

---

## 📊 Example Session Log

```json
{
  "room": "Business Strategy Discussion",
  "start_time": "2025-10-04T14:37:41",
  "conversation": [
    {"role": "user", "content": "Should we expand into Europe?"},
    {"role": "agent_1", "content": "Let's analyze the market data..."},
    {"role": "agent_2", "content": "We should also consider cultural adaptation..."},
    {"role": "agent_3", "content": "A bold but strategic move could involve..."}
  ]
}
```

---

## 🔬 Technical Highlights

- Sequential agent reasoning pipeline
- 65k-token context window for complex dialogue
- Automatic voice session handling
- Custom personality definition via JSON
- Full-stack SocketIO pipeline for real-time audio streaming

---

## 🎯 Future Enhancements

- 🌐 Multi-language support
- 🧠 Adaptive agent personalities (based on user tone)
- 🧩 Graph-based reasoning visualization
- 📈 Voice analytics dashboard
- 📱 Mobile-first responsive design

---

## 🏆 Hackathon Evaluation Alignment

| Criteria | AURA Strength |
|----------|---------------|
| **Potential Impact** | Introduces multi-agent reasoning for deeper AI-human collaboration |
| **Creativity & Originality** | Unique fusion of diverse AI personas interacting live |
| **Technical Implementation** | Advanced Cerebras API use, STT+TTS pipeline, real-time streaming |
| **Learning & Growth** | Built full-stack Dockerized AI orchestration from scratch |
| **Aesthetics & UX** | Intuitive, modern, and conversational web UI |
| **Presentation & Communication** | Clear live demo, session logs, and detailed documentation |

---

## 👨‍💻 Team

| Name | Role | Focus |
|------|------|-------|
| **Tarandeep Singh** | Developer | AI, Backend, Docker, Full-stack integration |

---

## 📜 License

This project is open-source and free for educational and research use.

---

## ❤️ Built With

- [Cerebras Cloud API](https://cloud.cerebras.ai/)
- [Meta Llama 3.3 70B](https://llama.meta.com/)
- [Deepgram STT/TTS](https://deepgram.com/)
- Flask + React + Docker Compose

---

**AURA isn't just an assistant — it's a conversation between minds.**  
**Experience it live →** [aura.kahlonai.com](https://aura.kahlonai.com)