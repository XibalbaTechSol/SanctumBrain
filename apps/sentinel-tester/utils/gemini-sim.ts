import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.NEXT_PUBLIC_GOOGLE_API_KEY || "");

export interface SimulationResult {
    slm_check: {
        pii_detected: boolean;
        redacted_message: string;
        reasoning: string;
    };
    vps_response: {
        intent: string;
        ui_payload: any;
        raw_response: string;
    };
}

export async function simulateNeuralFlow(userMessage: string): Promise<SimulationResult> {
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `
    You are simulating the neural orchestration flow of Sanctum Brain.
    User Message: "${userMessage}"

    Step 1: SLM (Small Language Model) PII Check.
    Check if the message contains sensitive data (emails, passwords, names, locations).
    
    Step 2: VPS (Frontier Model) Intent Extraction & UI Generation.
    If no PII or after redaction, determine intent and generate a JSON UI payload.
    Supported Intents: general_chat, system_health, weather_check, project_update.
    Supported Atoms: DiagnosticsCard, SystemHealthCard, InfoCard, RagVizCard.

    Return ONLY a JSON object in this exact format:
    {
        "slm_check": {
            "pii_detected": boolean,
            "redacted_message": "string",
            "reasoning": "string explaining what was found"
        },
        "vps_response": {
            "intent": "string",
            "ui_payload": {
                "intent": "string",
                "ui": {
                    "type": "AGUI_MANIFEST",
                    "layout": "GRID|STACK|BENTO",
                    "atoms": [
                        { "type": "AtomName", "props": { ... } }
                    ]
                }
            },
            "raw_response": "A professional synthesis of the request"
        }
    }
    `;

    try {
        const result = await model.generateContent(prompt);
        const text = result.response.text();
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (!jsonMatch) throw new Error("Invalid simulation response");
        return JSON.parse(jsonMatch[0]);
    } catch (err) {
        console.error("Simulation failed:", err);
        return {
            slm_check: { pii_detected: false, redacted_message: userMessage, reasoning: "Simulation fallback active." },
            vps_response: { intent: "error", ui_payload: null, raw_response: "Neural Link Latency High. Fallback engaged." }
        };
    }
}
