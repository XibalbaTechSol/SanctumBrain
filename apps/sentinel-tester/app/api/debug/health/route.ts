import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('http://localhost:8081/debug/health', {
      next: { revalidate: 0 } // Disable cache for health checks
    });
    
    if (!res.ok) {
      throw new Error(`Backend error: ${res.statusText}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[Debug API] Health Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
