# Objective
Architect a distributed autonomous agent ecosystem ("Sanctum Brain") as a unified monorepo containing Desktop/Web (Next.js/Tauri), Mobile (Flutter), and Backend (Python/LangGraph) with a PARA-based memory system.

# Monorepo Structure

```
SanctumBrain/
├── apps/
│   ├── backend/            # Repo C: Backend VPS (Python + LangGraph)
│   │   ├── app/            # LangGraph State Machine, Nodes, Tools
│   │   ├── proto/          # gRPC definitions
│   │   ├── main.py         # Entry point
│   │   └── requirements.txt
│   ├── web/                # Repo A: Desktop & Web Client (Next.js + Tauri)
│   │   ├── app/            # Next.js Pages & API routes
│   │   ├── components/     # Three.js Orb, AgentGraphView, A2UI Atoms
│   │   └── package.json
│   └── mobile/             # Repo B: Mobile Client (Flutter)
│       ├── lib/            # Nomad Interface, gRPC/WebSocket logic
│       └── pubspec.yaml
├── ops/                    # Orchestration & Deployment scripts
└── packages/               # Shared logic (e.g., db schemas)
```

## 2. LangGraph State Definition (Python)
Enhanced `AgentState` to support PARA and A2A-MCP flow.

```python
from typing import Annotated, Sequence, TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # CORE: Conversation history
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # PARA: Active memory pointers
    active_project_id: str
    active_area: str
    context_resources: List[str] # List of UUIDs to PARA Resources
    
    # INTENT: Derived from user input/activity
    intent: str # e.g., "UPDATE_PROJECT", "CREATE_RESOURCE"
    
    # PRIVACY: Local-first scrubbing status
    pii_redacted: bool
    
    # OUTPUT: MCP UI Payload for the client
    mcp_ui_payload: Dict[str, Any] 
    
    # AGENTIC LOOP: Reasoning steps for visualization
    reasoning_steps: List[str]
```

## 3. MCP Schema for UI-Payload Delivery
The backend sends a structured JSON that the client (Desktop/Mobile) interprets to render dynamic UI.

```json
{
  "mcp_version": "1.0",
  "intent": "PROJECT_MANAGEMENT",
  "ui": {
    "type": "PARA_DASHBOARD",
    "view": "KANBAN",
    "data": {
      "columns": ["To-Do", "In Progress", "Review", "Done"],
      "items": [
        { "id": "p1", "title": "Implement Tauri Shell", "status": "In Progress" }
      ]
    },
    "orb_state": {
      "color": "#4a90e2",
      "pulse": 1.2,
      "rotation_speed": 0.5
    }
  },
  "tools": [
    { "name": "add_task", "description": "Add task to active project" }
  ]
}
```

## 4. PARA Database Schema (SQL)
Normalized PostgreSQL schema for the "Frontier" node.

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    goal TEXT,
    deadline TIMESTAMP,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE areas (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    responsibility_level INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resources (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    content_type VARCHAR(50), -- 'DOC', 'LINK', 'CODE', 'MEDIA'
    content_payload JSONB,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archives (
    id UUID PRIMARY KEY,
    original_id UUID,
    original_type VARCHAR(50), -- 'PROJECT', 'AREA', 'RESOURCE'
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 5. Data Flow: Edge vs. Cloud (Physics-First)
- **Edge (Latency & Privacy):** 
  - User input/sensor data hits the **Desktop/Mobile** edge first.
  - Local LLM (llama.cpp/NPU) performs initial **intent classification** and **PII redaction** (Privacy-First).
  - Only anonymized intent + necessary metadata is sent to the **VPS** (Cloud).
- **Frontier (Reasoning Depth):** 
  - The VPS runs the **LangGraph loop** using high-parameter models (Claude/GPT).
  - It generates the **MCP UI Payload** and hydrates PARA context from the database.
- **Sync (Conflict Resolution):** 
  - State updates are pushed back via **WebSockets/gRPC SecureChannel**.
  - Local client merges the UI state into the 3D Orb and PARA views.

# Verification & Testing
1. **Mock Backend Test:** Run a Python script to verify the `mcp_ui_payload` generation logic.
2. **Visual Flow:** Ensure `AgentGraphView.tsx` correctly renders the new `PARA-Manager` node.
3. **Database Migration:** Validate the SQL schema with a test PostgreSQL container.
