# Energy Profile of the OpenClaw Loop (Physics-First Model)

In the Sanctum Brain ecosystem, we treat computation and attention as physical properties. The OpenClaw loop is modeled using a thermodynamic approach: **Information Flux ($dI/dt$) vs. Energy Cost ($E_c$)**.

## The OpenClaw Phases

The cognitive cycle consists of four distinct energetic states.

### 1. Observe (The Sensorium)
- **Action**: Ingestion of raw telemetry (mouse cadence, accelerometer data, microphone thresholds).
- **Latency ($\Delta t$)**: ~10-20ms.
- **Energy Cost ($E_c$)**: Near zero. Managed entirely by local client event loops.
- **Flux Type**: Continuous low-amplitude wave.
- **Orb Resonance**: Emerald Green, steady pulse (0.5 Hz).

### 2. Orient (The Local SLM)
- **Action**: Mapping physical sensor vectors into semantic intent.
- **Latency ($\Delta t$)**: ~300-600ms (Edge execution via llama.cpp or ONNX).
- **Energy Cost ($E_c$)**: Moderate. Consumes localized GPU/NPU cycles. Zero API token cost ($0).
- **Flux Type**: High-frequency, erratic burst (Context collapsing into a probability vector).
- **Orb Resonance**: Bright Blue, rapid chaotic spin (1.2 Hz).

### 3. Decide (The Frontier Neural Core)
- **Action**: Multi-agent deliberation, RAG retrieval, and LangGraph pathing.
- **Latency ($\Delta t$)**: ~1500-3000ms (Network round-trip + Frontier LLM inference).
- **Energy Cost ($E_c$)**: High. Consumes Gemini API tokens ($$$). This phase represents maximum "Cognitive Friction."
- **Flux Type**: Deep, dense standing wave. High data density, low velocity.
- **Orb Resonance**: Deep Violet, slow swirling vortex (0.3 Hz).

### 4. Act (The A2UI Render)
- **Action**: Expanding the decided schema into a visual 'Atom' on the Digital Canvas.
- **Latency ($\Delta t$)**: ~50-100ms (React DOM hydration).
- **Energy Cost ($E_c$)**: Low. Pure client-side UI rendering.
- **Flux Type**: Explosive radial expansion. The wavefunction collapses into a definitive state.
- **Orb Resonance**: Gold/White, high-intensity flash tied directly to token emission speed.

## The Self-Correction Heuristic
If the validation node detects an unstable payload during the 'Act' phase, it triggers an immediate re-orientation. 
This is modeled as **Cognitive Recoil**:
$$ E_{recoil} = \frac{1}{2} m v^2 $$
Where $m$ is the mass of the payload and $v$ is the speed of the error detection. Recoil forces the Orb into a jagged, chaotic Red state ($>2.0$ Hz) until equilibrium is restored by a successful graph traversal.
