import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('http://localhost:8081/debug/logs', {
      next: { revalidate: 0 } // Disable cache for logs
    });
    
    if (!res.ok) {
      throw new Error(`Backend error: ${res.statusText}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[Debug API] Logs Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
