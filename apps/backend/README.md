# SanctumBrain Backend: The Frontier Neural Core

The core server for the SanctumBrain ecosystem, responsible for multi-agent coordination, long-term memory retrieval (RAG), and dynamic AGUI state management.

## 🚀 Role in Ecosystem
- **Orchestrator**: Manages LangGraph state machines between supervisor, reasoner, and skill nodes.
- **Memory Provider**: Integrated OpenSearch vector store and PARA-based PostgreSQL memory.
- **Privacy Guardian**: Final PII audit and security egress before data leaves the VPS.
- **High-Perf Gateway**: Exposes gRPC and WebSocket endpoints for Desktop (Tauri) and Mobile (Flutter) clients.

## 🛠 Features
- **Dynamic Graph Orchestration**: Routing intent, reasoning steps, and security flags.
- **Model Context Protocol (MCP)**: Standardized tool-calling and resource discovery.
- **A2UI Flow**: Generates dynamic JSON payloads (AGUI) for client-side rendering.
- **The Pulse**: Periodic system telemetry hydration (CPU, RAM, Disk).

## 📂 Structure
- `app/`: Core LangGraph logic, nodes, and tool definitions.
- `proto/`: gRPC definitions for high-performance agent-to-agent communication.
- `soul/`: Base personality and core directives for the orchestrator.
- `skills/`: Modular agentic capabilities (Shell, File, PARA Manager).

## 🚀 Setup & Execution

### 1. Requirements
- Python 3.10+
- Docker & Docker Compose (for PostgreSQL, OpenSearch, Redis)

### 2. Environment Configuration
Create a `.env` file with your credentials:
```env
DATABASE_URL=postgres://user:password@localhost:5432/sanctum_brain
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

### 3. Start Infrastructure
```bash
docker-compose up -d
```

### 4. Run the Server
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py serve
```

---
*Distributed Intelligence for the Sovereign Workspace.*
