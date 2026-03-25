import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || '');
const geminiModel = genAI.getGenerativeModel({ model: 'gemini-1.5-flash-latest' });

export async function POST(req: NextRequest) {
  try {
    const { ui_payload } = await req.json();

    if (!ui_payload) {
      return NextResponse.json({ error: 'No UI payload provided' }, { status: 400 });
    }

    if (ui_payload.html) {
      return NextResponse.json({ html: ui_payload.html });
    }

    const prompt = `
      You are the Sanctum Neural Core UI Architect. Generate an ultra-modern, dynamic, and immersive HTML5 document.
      
      AGUI Manifest: ${JSON.stringify(ui_payload, null, 2)}
      
      Aesthetic Mandates:
      - **Design Style**: Choose from [Bento Grid, Neo-Brutalism, Minimalist Cyberpunk, or Glassmorphism]. Variate the style based on the intent.
      - **Color Palette**: Deep blacks (#000), rich indigos, electric cyans, and occasional high-contrast accents (lime, magenta).
      - **Backgrounds**: Use sophisticated mesh gradients, animated noise textures, or subtle moving grid lines.
      - **Typography**: Expansive, bold, high-tracking uppercase headers. Use variable font weights for hierarchy.
      
      Technical Requirements:
      1. **Self-Contained**: Full <!DOCTYPE html> with Tailwind, Lucide, Chart.js, and Animate.css.
      2. **Interactive State**: Use Vanilla JS to manage complex internal states (e.g., tabs, progressive disclosures, interactive data filters).
      3. **Micro-interactions**: Every button and card must have a sophisticated hover state (glow, slight scale, tilt effect).
      4. **Staggered Animations**: Use Animate.css or custom CSS transitions to stagger the entry of elements.
      5. **Data Viz**: If metrics exist, use Chart.js with custom gradients and no-gridline minimalist styling.
      
      Layout:
      - **FULL SCREEN**: html, body { height: 100%; width: 100%; margin: 0; padding: 0; overflow: hidden; background: #000; }
      - Root: "h-full w-full flex flex-col p-8 md:p-16 overflow-y-auto"
      
      Intent: "${ui_payload.intent}"
      
      Output ONLY raw HTML code. Do not wrap in markdown blocks. No preamble. Make it feel like a premium sovereign OS interface.
    `;

    try {
      const result = await geminiModel.generateContent(prompt);
      const response = await result.response;
      const html = response.text().replace(/```html|```/g, '').trim();
      return NextResponse.json({ html });
    } catch (geminiError: any) {
      console.error(`[Sentinel Render] Google SDK Failed: ${geminiError.message}`);
      // ULTIMATE INTERACTIVE FALLBACK
      const fallbackHtml = `
          <!DOCTYPE html>
          <html style="height: 100%; width: 100%;">
            <head>
              <script src="https://cdn.tailwindcss.com"></script>
              <script src="https://unpkg.com/lucide@latest"></script>
              <style>
                body { margin: 0; padding: 0; background: #000; color: white; font-family: sans-serif; height: 100%; width: 100%; overflow: hidden; }
                .glass { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); }
                .active-tab { background: rgba(79, 70, 229, 0.2); border-color: rgba(79, 70, 229, 0.5); color: #818cf8; }
              </style>
            </head>
            <body>
              <div class="h-full w-full flex flex-col p-12 bg-slate-950">
                <div class="flex justify-between items-center mb-12">
                  <div>
                    <h1 class="text-6xl font-black tracking-tighter uppercase italic">Neural Sentinel</h1>
                    <p id="system-status" class="text-indigo-400 font-mono text-sm uppercase tracking-[0.5em]">Status: IDLE</p>
                  </div>
                  <div class="flex gap-4">
                    <button id="protocol-balanced" onclick="setProtocol('BALANCED')" class="glass px-6 py-2 rounded-xl text-[10px] font-bold active-tab">BALANCED</button>
                    <button id="protocol-aggressive" onclick="setProtocol('AGGRESSIVE')" class="glass px-6 py-2 rounded-xl text-[10px] font-bold">AGGRESSIVE</button>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-8 flex-1">
                  <div class="glass rounded-[3rem] p-10 flex flex-col justify-center items-center space-y-8">
                    <div id="status-orb" class="w-32 h-32 rounded-full border-4 border-indigo-500/30 flex items-center justify-center transition-all duration-500">
                       <i data-lucide="shield" class="w-12 h-12 text-indigo-500"></i>
                    </div>
                    <button id="scan-btn" onclick="startScan()" class="w-full max-w-xs py-6 bg-indigo-600 rounded-3xl font-black tracking-widest uppercase hover:bg-indigo-500 transition-all shadow-2xl">Initialize Scan</button>
                  </div>
                  
                  <div class="glass rounded-[3rem] p-10 relative">
                    <h3 class="text-xl font-bold mb-6">Action Logs</h3>
                    <div id="logs" class="font-mono text-xs text-indigo-300/60 space-y-2">
                       <p>&gt; Sentinel Node ready for command.</p>
                    </div>
                    
                    <button id="deploy-btn" onclick="showModal()" class="absolute bottom-10 right-10 p-6 rounded-2xl bg-emerald-600 font-black uppercase text-xs tracking-widest opacity-30 cursor-not-allowed transition-all" disabled>Deploy Config</button>
                  </div>
                </div>

                <div id="modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md hidden">
                   <div class="glass p-12 rounded-[3rem] text-center max-w-md border-indigo-500/50">
                      <h2 class="text-3xl font-black mb-4">Confirm?</h2>
                      <p class="text-sm text-slate-400 mb-8">Execute lockdown protocol across all nodes?</p>
                      <div class="flex gap-4">
                         <button onclick="hideModal()" class="flex-1 py-4 rounded-2xl glass font-bold">Abort</button>
                         <button id="confirm-btn" onclick="confirmDeploy()" class="flex-1 py-4 rounded-2xl bg-indigo-600 font-bold">Confirm</button>
                      </div>
                   </div>
                </div>
              </div>

              <script>
                lucide.createIcons();
                function addLog(msg) {
                  const logs = document.getElementById('logs');
                  const p = document.createElement('p');
                  p.innerHTML = '> ' + msg;
                  logs.prepend(p);
                }
                function setProtocol(type) {
                  document.querySelectorAll('button[id^="protocol-"]').forEach(b => b.classList.remove('active-tab'));
                  document.getElementById('protocol-' + type.toLowerCase()).classList.add('active-tab');
                  addLog('Security protocol set to ' + type);
                }
                function startScan() {
                  const btn = document.getElementById('scan-btn');
                  const orb = document.getElementById('status-orb');
                  btn.disabled = true;
                  btn.innerText = 'Scanning...';
                  orb.classList.add('animate-pulse', 'border-indigo-500');
                  addLog('Deep scan initiated...');
                  setTimeout(() => {
                    btn.innerText = 'Scan Complete';
                    document.getElementById('system-status').innerText = 'Status: READY';
                    document.getElementById('deploy-btn').classList.remove('opacity-30', 'cursor-not-allowed');
                    document.getElementById('deploy-btn').disabled = false;
                    addLog('Vulnerabilities mitigated. Ready for deployment.');
                  }, 2000);
                }
                function showModal() { document.getElementById('modal').classList.remove('hidden'); }
                function hideModal() { document.getElementById('modal').classList.add('hidden'); }
                function confirmDeploy() {
                  hideModal();
                  document.querySelector('h1').innerText = 'SECURE';
                  document.getElementById('system-status').innerText = 'Status: LOCKED';
                  document.body.style.background = '#020617';
                  addLog('Global deployment successful.');
                }
              </script>
            </body>
          </html>
        `;
      return NextResponse.json({ html: fallbackHtml });
    }
  } catch (error: any) {
    console.error('[Sentinel API] Outer Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
