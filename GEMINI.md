# Sanctum Brain: Project Memory & Progress

**Goal:** Build a Sovereign Agentic Workspace that competes with Enterprise Browsers by offering personal ownership, private VPS-based infrastructure, and proactive "always-on" intelligence.
## 🚀 Active Task
- **Phase 4: Scaling & Autonomous Refinement** -> Enhancing multi-agent coordination and implementing self-healing UI patterns.

## 📊 Implementation Progress

### Phase 1: Architecture & Scaffolding
- [x] Task 1: Monorepo & Environment Setup
    - [x] Initial directory structure created.
    - [x] Configure `Sanctum Guard VPS` Docker stack.
    - [x] Setup gRPC/Proto definitions (`apps/backend/proto/a2a.proto`).
- [x] Task 2: OpenClaw Core Integration
    - [x] Scaffold `SOUL.md` in `apps/backend/soul/`.
    - [x] Initialize `skills/` directory and basic skills (Shell, File).
    - [x] Port ReAct loop logic (`apps/backend/app/graph.py` and `nodes.py`).

### Phase 2: The Sovereign Interface
- [x] Task 3: The 3D Orb & Voice Gateway
    - [x] Integrate Three.js Orb component (`apps/web/components/Orb/`).
    - [x] Connect WebSocket/gRPC client to backend (`/ws/voice` endpoint).
- [x] Task 4: Predictive UI (A2UIRenderer)
    - [x] Create `A2UIRenderer` component and sub-cards (`InfoCard`, `WeatherCard`, `RagVizCard`).
    - [x] create `/api/chat` proxy route.
    - [x] Refactor `FloatingInbox` into a predictive chat interface.

### Phase 3: Intelligence & Memory
- [x] Task 5: Agentic Memory (OpenRAG)
    - [x] Implement `retrieve_context` in `rag.py` with OpenSearch (`opensearch-py`).
    - [x] Create ingestion endpoint (`/router/upload_ingest`) in `main.py`.
    - [x] Connect Frontend Inbox to Ingestion Pipeline.
- [x] Task 6: Multi-Channel Command Center
    - [x] LangGraph state established as the **Source of Truth** for the entire system.
    - [x] Integrated system health metrics (CPU, RAM, Disk) into the graph state.
    - [x] Created `AgentGraphView` (`reactflow`) to visualize the orchestration loop.
    - [x] Implemented `SystemHealthCard` in the A2UI renderer.

### Phase 4: Scaling & Autonomous Refinement
- [x] Task 7: Autonomous Refinement
    - [x] Implement self-healing UI patterns and comprehensive playwright validation (Sidebar, Themes, AI Providers).
    - [x] Optimize LangGraph routing for lower latency.
- [x] Task 8: Multi-Agent Coordination
    - [x] Refine PARA-Manager for cross-agent project synchronization.
    - [x] Integrate local SLM for PII redaction on-device.
## 🧠 Architectural Decisions
1. **Sovereign VPS First:** All heavy compute and intelligence resides on a user-owned VPS (Sanctum Guard) to ensure data privacy.
2. **Hybrid Agentic Loop:** Combines `OpenClaw` ReAct patterns for local execution with `LangGraph` for complex multi-agent orchestration. **The Graph is the Source of Truth.**
3. **Predictive UI:** Interfaces are generated dynamically via `A2UIRenderer` based on intent, rather than using static dashboards.
4. **Local-First Security:** Use a `LocalLLMService` on-device to redact PII before sending context to the VPS.
5. Unified Pulse: The system periodically hydrates its status into the agent's memory, allowing for proactive assistance.
6. **UI/UX Validation Strategy:** Every prompt involving UI/UX changes or automated testing MUST conclude with the generation/update of a dedicated HTML summary report (hosted in `apps/web/public/test-results/`) containing high-fidelity screenshots of the successful state and a detailed fix-log of any remediations performed.

## 🛠 Tech Stack
- **Frontend:** Next.js 15, Tailwind CSS 4, React Flow, Three.js (Orb).
- **Backend:** Python (FastAPI, LangGraph), Node.js (Voice/WebSocket).
- **Database:** OpenSearch (Vector), PostgreSQL (Structured), Redis (Events).
- **Communication:** gRPC (High-perf), WebSocket (Real-time).
