# Sentinel A2A Tester

This is an independent testing application built for the SanctumBrain ecosystem to validate the **A2A (Agent-to-Agent)**, **A2UI (Agent-to-User Interface)**, and **AGUI (Agentic GUI)** tech stack.

## 🚀 Purpose
To ensure that the "Sovereign Intelligence" can communicate its intent across the neural core and render dynamic, generative interfaces on the client-side using a "Local LLM" (simulated via Gemini).

## 🛠 Features
- **A2A Pulse Matrix:** A bidirectional (simulated) communication channel to the Sanctum VPS Backend.
- **AGUI Manifest Decoder:** Automatically parses and Decrypts the Agentic GUI payloads.
- **Local LLM Renderer:** A sandboxed environment that uses an LLM to generate React/Tailwind code on-the-fly from AGUI definitions.
- **Neural Trace Logging:** A unified panel that traces every step of the agentic loop:
  - `Intent` -> `A2A Packet` -> `AGUI JSON` -> `LLM Code` -> `Render`.
- **Advanced Debugging Suite:** A dedicated panel for deep system investigation:
  - **Neural Log Stream**: Real-time streaming of the Sanctum VPS `system.log`.
  - **AGUI Manual Injector**: Directly test the renderer by injecting raw JSON AGUI payloads.
  - **System Heartbeat**: Monitor connectivity to Redis and Ollama.

## 📂 Architecture
- **Tech Stack:** Next.js, Framer Motion, Tailwind CSS, Lucide Icons.
- **Backend Bridge:** Connects to `localhost:8081` (The Sanctum REST Proxy).
- **Generative Sandbox:** Uses the `IframeSandbox` to execute LLM-generated React code safely.

## 🚦 Getting Started
1. Ensure the SanctumBrain Backend is running (`./apps/backend/start_vps.sh` or `npm run dev` in backend root).
2. Set your Google API Key: `export GOOGLE_API_KEY=YOUR_KEY` (Required for full generative rendering).
3. Run the tester:
   ```bash
   ./apps/sentinel-tester/start_sentinel.sh
   ```
4. Access at `http://localhost:3001`.

## 🧩 Validation Traces
- **A2A:** Validates the message and intent exchange format.
- **A2UI:** Tests the predictive UI routing and manifest extraction.
- **AGUI:** Verifies compliance with the Sanctum Brain GUI JSON Schema.
- **ACM:** Tests the local context management (ACM) v1.0.1.
