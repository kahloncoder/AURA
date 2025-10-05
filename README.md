# AURA: Live Council of AI Experts for Collective Intelligence

> **Live Demo:** [🌐 aura.kahlonai.com](https://aura.kahlonai.com)  
> **Built for FutureStack GenAI Hackathon** — powered by **Cerebras**, **Meta Llama**, and **Docker**

---

## 🧠 Overview

**AURA** is an AI-powered **live council of experts** that simulates real human deliberation — three specialized AI experts listen to each other, debate perspectives, and build on one another's insights to deliver the most complete understanding possible.

It's not just a voice assistant — it's a **panel of experts thinking together in real-time**.

Built using:
- **Cerebras Cloud API** for ultra-fast inference with **Llama 3.3 (70B)**
- **Deepgram** for real-time voice input/output
- **Flask + React + Socket.IO** for seamless real-time communication
- **Docker Compose** for one-command deployment across backend, frontend, and MongoDB

---

## 🚀 Why AURA?

Modern AI assistants give you a single perspective — analytical, empathetic, or creative — but never a **deliberation between all three**.

AURA creates a **live council** where:
- Each expert **hears and responds** to previous experts
- Perspectives **compound and evolve** through genuine interaction
- Expert 3 **synthesizes** insights from Experts 1 and 2
- Every room develops **unique chemistry** based on specialized knowledge areas

This makes AURA ideal for:
- **Complex decisions** requiring multiple viewpoints
- **Brainstorming** where perspectives build on each other
- **Strategy discussions** with analytical + creative synthesis
- **Emotional support** with empathetic + practical guidance
- **Educational scenarios** showing expert deliberation

You're not getting three separate answers — you're witnessing a **real council deliberation**.

---

## 🌍 Tech Stack

| Layer | Technology | Description |
|-------|-------------|-------------|
| 🧠 LLM | **Cerebras Cloud (Llama 3.3 70B)** | Core intelligence for all experts |
| 🔊 Speech | **Deepgram STT + TTS** | Real-time voice transcription & synthesis |
| ⚙️ Backend | **Flask + Socket.IO** | Orchestrates expert deliberation & sessions |
| 💻 Frontend | **React** | Interactive dashboard for council sessions |
| 🐋 Deployment | **Docker Compose** | Scalable multi-service setup |
| 🗄️ Database | **MongoDB (optional)** | Persistent storage for council sessions |

---

## ⚡ Hackathon Relevance

| Sponsor | Integration | Hack Value |
|----------|--------------|-------------|
| **Cerebras** 🧠 | Used for fast, large-context inference (Llama 3.3 70B) enabling real-time expert deliberation | Demonstrates sequential reasoning where each expert processes full council context |
| **Meta** 💬 | Leverages open-source **Llama models** for distinct expert personalities that genuinely interact | Showcases collaborative AI where perspectives build on each other |
| **Docker** 🐋 | Full **Docker Compose** setup (frontend + backend + MongoDB) | Enables reproducible, cloud-native deployment of the entire expert system in one command |

---

## 💡 Core Innovation

### 🎙️ Live Council Architecture

AURA creates **three AI experts** who don't just take turns speaking — they **listen, respond, and build on each other's perspectives**.

```
User (Voice Input)
        ↓
  Deepgram STT
        ↓
Expert 1 (Analytical) → Shares initial perspective
        ↓
Expert 2 (Empathetic) → Hears Expert 1, adds human factors
        ↓
Expert 3 (Creative) → Hears both, synthesizes final insight
        ↓
Consensus Generation
        ↓
Deepgram TTS (Voice Output)
```

**Key Innovation:** Each expert receives the **full council context** — Expert 2 explicitly references Expert 1's points, and Expert 3 synthesizes contradictions or builds connections between the first two perspectives.

This creates **genuine collaboration**, not parallel responses.

---

### 🧩 Architecture Diagram

```
            ┌──────────────────────────┐
            │        Frontend          │
            │   (React + Socket.IO)    │
            │  Live Council Interface  │
            └────────────┬─────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     Flask API        │
              │   Council Orchestrator│
              │  (Expert 1→2→3 Flow) │
              └───────┬──────────────┘
                      │
         ┌────────────┴──────────────┐
         │  Voice I/O (Deepgram)     │
         │  Expert Context Passing   │
         │  Cerebras API (Llama 3.3) │
         │  Session Logging (JSON)   │
         └────────────┬──────────────┘
                      │
                      ▼
            MongoDB (Council History)
```

---

## 🧰 Features

- 🎙 **Voice-driven council sessions** (no typing needed)
- 🧩 **3-Expert deliberation** (analytical + empathetic + creative)
- 🔗 **Context-aware interaction** (each expert hears the others)
- 🧠 **Perspective synthesis** (Expert 3 combines insights)
- 🕒 **Timed sessions** with automatic logging
- 🗃 **Full deliberation logs** saved as JSON
- 🧍‍♂️ **Unique room chemistry** (editable expert profiles in `rooms.json`)
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

## 🎮 How The Council Works

1. 🎤 **User asks a question via voice**
2. 🧏 **Deepgram converts speech to text**
3. 🧠 **Expert 1 (Analytical)** provides data-driven perspective
4. 👂 **Expert 2 (Empathetic)** listens to Expert 1, adds human factors
5. 💡 **Expert 3 (Creative)** hears both experts, synthesizes final insight
6. 🔊 **AURA speaks the collective council response**

**Critical Feature:** Each expert's prompt includes the previous experts' responses, enabling genuine deliberation where perspectives build on each other.

Each council session is auto-saved under `/backend/logs/`.

---

## 🎨 UX & Design

- Modern minimal UI showing live council status
- Real-time transcription of each expert's contribution
- Visual indicators: **Expert 1 Thinking** → **Expert 2 Speaking** → **Expert 3 Synthesizing**
- Session summary showing how perspectives evolved
- Dark/light theme ready

---

## 📊 Example Council Session Log

```json
{
  "room": "Business Strategy Council",
  "start_time": "2025-10-04T14:37:41",
  "deliberation": [
    {
      "role": "user", 
      "content": "Should we expand into Europe?"
    },
    {
      "role": "expert_1_analytical", 
      "content": "Based on market data, European expansion shows 23% growth potential but requires €2M initial investment..."
    },
    {
      "role": "expert_2_empathetic", 
      "content": "I hear Expert 1's data concerns. We should also consider our team's readiness—cultural adaptation takes 6-12 months..."
    },
    {
      "role": "expert_3_creative", 
      "content": "Building on both perspectives: What if we pilot in one country first? This addresses Expert 1's investment concerns while giving us the cultural learning Expert 2 mentioned..."
    }
  ]
}
```

---

## 🔬 Technical Highlights

- **Sequential expert pipeline** with cumulative context passing
- **65k-token context window** for complex multi-turn deliberations
- **Automatic voice session handling** with real-time streaming
- **Custom expert personalities** via JSON configuration
- **Full-stack SocketIO pipeline** for real-time audio
- **Context-aware prompting** where each expert explicitly references colleagues

---

## 🎯 What Makes This Unique

### 🔗 Genuine Expert Interaction
Unlike traditional multi-agent systems where agents work in parallel, AURA's experts **sequentially build on each other**:
- Expert 2's prompt includes: *"Expert 1 said: [their response]. Now add your perspective..."*
- Expert 3's prompt includes: *"Expert 1 analyzed... Expert 2 considered... Now synthesize..."*

### 🧪 Dynamic Room Chemistry
Each room configuration creates different expert dynamics:
- **Business Strategy Room**: Analytical + Risk-Aware + Growth-Focused
- **Creative Brainstorm Room**: Logical + Emotional + Visionary
- **Personal Advice Room**: Practical + Empathetic + Motivational

### 🎭 Perspective Synthesis
Expert 3 doesn't just add a third opinion — they actively:
- Identify contradictions between Expert 1 and 2
- Find common ground across perspectives
- Create actionable paths that honor all viewpoints

---

## 🎯 Future Enhancements

- 🌐 Multi-language council support
- 🧠 Adaptive expert personalities based on user tone
- 🧩 Graph visualization of how perspectives evolved
- 📈 Council analytics dashboard
- 🎭 User-customizable expert profiles
- 📱 Mobile-first responsive design

---

## 🏆 Hackathon Evaluation Alignment

| Criteria | AURA Strength |
|----------|---------------|
| **Potential Impact** | Introduces collaborative AI deliberation for complex decision-making |
| **Creativity & Originality** | First voice assistant where AI experts genuinely listen and respond to each other |
| **Technical Implementation** | Advanced context passing, real-time voice streaming, sequential reasoning pipeline |
| **Learning & Growth** | Built full-stack expert orchestration system from scratch with Docker |
| **Aesthetics & UX** | Intuitive council interface showing live expert interactions |
| **Presentation & Communication** | Clear live demo, detailed session logs, comprehensive documentation |

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

**AURA isn't just an assistant — it's a live council of experts who deliberate together.**  
**Experience the council →** [aura.kahlonai.com](https://aura.kahlonai.com)
