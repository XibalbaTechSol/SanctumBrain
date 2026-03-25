# Sanctum Brain Architecture

## Overview
Sanctum Brain is a Sovereign Agentic Workspace designed to offer personal ownership, private VPS-based infrastructure, and proactive "always-on" intelligence.

The architecture is distributed across four major components:
1. **VPS (Sanctum Guard)**: The heavy-compute backend orchestrating LangGraph state machines, structured Postgres databases (PARA methodology), and OpenSearch vector intelligence.
2. **Desktop (Digital Canvas)**: A Tauri-based skeleton providing local system access, high-performance rendering via React/Three.js, and offline capabilities.
3. **Mobile (Nomad Interface)**: A Flutter application that connects to the VPS via WebSockets, allowing mobile-native interaction.
4. **Orchestration & Discovery**: Local network and Tailscale integration to securely bind the client nodes to the sovereign VPS.

## Distributed Intelligence Model
Sanctum Brain follows a "Frontier + Edge" intelligence pattern:

1. **Frontier Neural Core (VPS)**:
   - **Model**: Google Gemini (primary reasoning engine).
   - **Role**: Complex multi-agent orchestration, long-term memory retrieval (RAG), and code generation.
   - **Justification**: High-compute requirements and access to the global knowledge graph.

2. **Edge SLM (Desktop & Mobile)**:
   - **Model**: Small Language Model (SLM) like Phi-3, Llama-3-8B, or Mistral-7B (running via llama.cpp or local providers).
   - **Role**: PII Redaction (Privacy-First), intent pre-classification, and rapid "Kinetic" UI feedback.
   - **Justification**: Zero-latency local execution, guaranteed data privacy (PII never leaves the device), and offline capability for basic system tasks.

## A2UI (Agent-to-User Interface) Flow
The traditional paradigm of static dashboards is replaced by the A2UI flow. In this model:
- The system lacks static, predefined routes.
- The UI is dynamically generated based on continuous state monitoring and user intent.
- When an intent is detected, the LangGraph orchestrator streams a JSON payload (AGUI Schema) to the client.
- The client-side `A2UIRenderer` maps this schema to UI atoms (e.g., `InfoCard`, `SystemHealthCard`, `RagVizCard`), rendering the interface on demand.

## The Pulse (Security Ingress)
Every interaction begins with **The Pulse** (`security_ingress` node). This node performs two critical functions:
1. **System Ingestion**: It hydrates the current LangGraph state with real-time telemetry (CPU, RAM, Disk, and active process tree).
2. **PII Redaction**: It scans incoming user prompts for personally identifiable information (PII) before the data reaches the higher-parameter Frontier models on the VPS. This ensures a "Privacy-First" approach by redacting credentials, names, or locations at the entry point.

## Dynamic Graph Orchestration
Unlike static logic trees, Sanctum Brain's backend is a dynamic state machine controlled via `graph_config.json`. This allows the system to:
- **Hot-Swap Nodes**: New agentic skills can be added by simply updating the JSON config without restarting the server.
- **Conditional Routing**: The `dynamic_router` evaluates intent, reasoning steps, and security flags to determine the optimal path (e.g., routing to `rag` for knowledge retrieval or `para_manager` for project updates).
- **Self-Healing Traversal**: If a node fails or an intent is ambiguous, the graph defaults to a `generator` or `reasoner` node to clarify or provide a graceful fallback UI.

## AGUI (Agentic GUI) JSON Schema
AGUI is the protocol linking the LangGraph orchestrator to the client renderer. A standard AGUI payload follows this structure:

```json
{
  "type": "agui_render",
  "intent": "system_health_check",
  "urgency": "low",
  "atoms": [
    {
      "component": "SystemHealthCard",
      "props": {
        "cpu": 45,
        "ram": 60,
        "status": "healthy"
      }
    },
    {
      "component": "ActionButtons",
      "props": {
        "actions": ["optimize", "dismiss"]
      }
    }
  ],
  "layout": "minimalist"
}
```

## Physics-Based Context & UI Wavefunction Collapse
To bridge the gap between human kinetic input and agentic processing, we use **Sensor Fusion**.
- **The Wavefunction**: Before the user performs an action, the system maintains a probabilistic map of possible intents (the "UI Wavefunction").
- **Sensor Fusion**: High-velocity mouse movements, window focus changes, microphone activation patterns, and environmental contexts (time of day, location) act as "observations."
- **Collapse**: These observations collapse the wavefunction. For example, a sudden, rapid mouse swipe to the edge of the screen combined with an active code editor instantly collapses the UI to display the "Minimalist Code Assist" atom, bypassing complex navigation.

## Model Context Protocol (MCP) Integration
Sanctum Brain utilizes the Model Context Protocol (MCP) to standardize tool-calling.
- **Discovery**: Clients automatically discover the VPS MCP Server via mDNS or Tailscale MagicDNS.
- **Capabilities**: The VPS exposes tool definitions (e.g., `execute_query`, `read_vector_store`, `manage_docker`) over the MCP transport layer.
- **Client Execution**: The Desktop and Mobile clients can act as MCP hosts, routing local tool calls (like reading local files) back to the VPS for secure processing.