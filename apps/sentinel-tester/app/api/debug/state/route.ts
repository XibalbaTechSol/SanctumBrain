import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const threadId = req.nextUrl.searchParams.get('threadId') || 'rest-session';
    const res = await fetch(`http://localhost:8081/debug/state/${threadId}`, {
      next: { revalidate: 0 }
    });
    
    if (!res.ok) {
      throw new Error(`Backend error: ${res.statusText}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('[Debug API] State Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
