# SanctumBrain 🧠: The Sovereign Agentic Workspace

SanctumBrain is a private, distributed AI ecosystem designed for personal ownership and proactive intelligence. It moves beyond static dashboards into a "Frontier + Edge" model where your data stays on your own infrastructure.

## 🏗️ Architecture

- **Frontier Neural Core (VPS/Sanctum Guard)**: A high-compute backend orchestrating LangGraph state machines, OpenSearch vector intelligence, and PARA-based structured memory.
- **Digital Canvas (Desktop/Sentinel)**: A Tauri-based interface providing local system access, high-performance Three.js rendering, and offline PII redaction.
- **Nomad Interface (Mobile)**: A Flutter application for secure, mobile-native access to your sovereign brain via gRPC/WebSockets.

## 📂 Monorepo Structure

- `/apps/backend`: Python/FastAPI/LangGraph orchestration engine.
- `/apps/web`: Next.js 15 web interface and VPS management dashboard.
- `/apps/mobile`: Flutter mobile client logic.
- `/hermes`: Core Hermes Agent framework integration.
- `/agency`: 140+ specialized expert personas for delegation.
- `/ops`: Unified deployment and orchestration scripts.

## 🚀 Quick Start

### 1. Launch the Ecosystem
Use the unified startup script to bring both the backend and web interfaces online:
```bash
./ops/start_ecosystem.sh
```

### 2. Manual Backend Setup
```bash
cd apps/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py serve
```

## 🛡️ Privacy & Security
- **PII Redaction**: All user input is scrubbed for personally identifiable information at the edge before reaching frontier models.
- **Sovereign VPS**: You own the infrastructure; your data never trains public models.
- **The Pulse**: Real-time telemetry monitoring for system health and security.

## 🛠 Tech Stack
- **AI**: LangGraph, Gemini 2.0, Hermes 3, The Agency.
- **Frontend**: Next.js 15, Tailwind CSS 4, React Flow, Three.js.
- **Backend**: FastAPI, gRPC, Tortoise ORM.
- **Data**: OpenSearch (Vector), PostgreSQL (PARA), Redis.

---
*Built with a Physics-First approach to autonomous intelligence.*
