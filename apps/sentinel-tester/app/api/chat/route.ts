import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { message, inferred_intent } = body;

    // Call the SanctumBrain backend (REST Bridge) with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    const res = await fetch('http://localhost:8081/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        inferred_intent: inferred_intent || 'general_chat',
        device_id: 'sentinel-tester'
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      throw new Error(`Backend error: ${res.statusText}`);
    }

    const data = await res.json();
    
    // Log the A2A trace (Simulated)
    const logIntent = inferred_intent || 'general (inferred)';
    console.log(`[A2A TRACE] Intent: ${logIntent}`);
    console.log('[A2A TRACE] Response Received from SanctumBrain');

    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[Sentinel API] Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
