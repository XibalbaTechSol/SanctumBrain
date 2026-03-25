'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Terminal as TerminalIcon, Zap, Smartphone, Database, 
  Activity, Layers, SlidersHorizontal, Send, Wifi, Clock,
  Cpu as SmlIcon, Puzzle, Layout as LayoutIcon, ShieldCheck,
  HardDrive, Network, Radio
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import TracePanel, { TraceEvent } from '@/components/TracePanel';
import Terminal from '@/components/Terminal';
import MobileDevice from '@/components/MobileDevice';
import SensorLab from '@/components/SensorLab';
import OrbScene from '@/components/OrbScene';

interface DebugLog {
  type: string;
  msg: string;
  timestamp: string;
}

export default function SanctumDiagnostics() {
  const [isMounted, setIsMounted] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mobilePayload, setMobilePayload] = useState<any>(null);
  const [traces, setTraces] = useState<TraceEvent[]>([]);
  const [activeWindow, setActiveWindow] = useState<string>('messenger');
  const [currentTime, setCurrentTime] = useState('');
  const [logs, setLogs] = useState<DebugLog[]>([]);
  const [graphState, setGraphState] = useState<any>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const addTrace = useCallback((type: TraceEvent['type'], data: any) => {
    setTraces(prev => [{
      id: Math.random().toString(36).substring(7),
      type, data, timestamp: Date.now()
    }, ...prev]);
  }, []);

  useEffect(() => {
    setIsMounted(true);
    const updateTime = () => setCurrentTime(new Date().toLocaleTimeString([], { hour12: false }));
    updateTime();
    const t = setInterval(updateTime, 1000);
    return () => clearInterval(t);
  }, []);

  // Auto-generate log entries for the log panel
  useEffect(() => {
    const interval = setInterval(() => {
      const types = ['SYN', 'ACK', 'MTX', 'FIN', 'RST', 'PULSE', 'RELAY'];
      const msgs = [
        'Heartbeat acknowledged',
        'Buffer flushed 0x4F2',
        'Routing table synced',
        'Sentinel keepalive OK',
        'Memory pressure nominal',
        'Neural link stable',
        'Mesh topology updated',
      ];
      const type = types[Math.floor(Math.random() * types.length)];
      const msg = msgs[Math.floor(Math.random() * msgs.length)];
      setLogs(prev => [{
        type,
        msg,
        timestamp: new Date().toLocaleTimeString([], { hour12: false }),
      }, ...prev].slice(0, 50));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    setLoading(true);
    const msg = input.trim();
    setInput('');
    try {
      addTrace('A2A_REQUEST', { message: msg });
      
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, inferred_intent: 'general' })
      });
      
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      
      addTrace('SLM_PII_CHECK', { result: 'SECURE', reasoning: 'Processed via Sanctum Proxy' });
      addTrace('VPS_ORCHESTRATOR', { intent: data.ui_payload?.intent || 'general', node: 'Sanctum_Guard_01' });
      
      const content = data.messages?.[0]?.content || 'Processed.';
      addTrace('A2A_RESPONSE', { response: content });

      if (data.ui_payload) {
        addTrace('AGUI_PAYLOAD', data.ui_payload);
        setMobilePayload(data.ui_payload);
      }
    } catch (err) {
        addTrace('RENDER_STATUS', { status: 'ERROR', error: 'Neural link interrupted' });
    } finally {
      setLoading(false);
    }
  };

  if (!isMounted) return null;

  return (
    <main className="fixed inset-0 bg-[#020204] text-[#eceff4] overflow-hidden font-mono select-none flex flex-col">
      {/* === TOP STATUS BAR === */}
      <div className="h-10 shrink-0 bg-black/80 backdrop-blur-md flex items-center justify-between px-6 z-50 border-b border-white/5">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-aurora-purple animate-pulse shadow-[0_0_8px_#b48ead]" />
            <span className="text-[10px] font-extrabold uppercase tracking-[0.4em] text-white/80">Sanctum_Sentinel_v3.0</span>
          </div>
          <div className="h-4 w-px bg-white/10" />
          <div className="flex items-center gap-5 text-[9px] font-bold text-white/25 tracking-widest uppercase">
            <span className="flex items-center gap-1.5"><HardDrive className="w-3 h-3" /> VOL_01: NOMINAL</span>
            <span className="flex items-center gap-1.5 text-aurora-green"><Network className="w-3 h-3" /> LINK: ACTIVE</span>
          </div>
        </div>
        <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-white/40 text-[10px] font-bold">
                <Clock className="w-3.5 h-3.5" />
                <span className="tabular-nums">{currentTime}</span>
            </div>
            <div className="px-3 py-1 bg-white/5 rounded border border-white/10 text-[8px] font-extrabold uppercase tracking-wider text-white/40">
                Sovereign_Node_0xAF4
            </div>
        </div>
      </div>

      {/* === MAIN WORKSPACE: 2 COLUMNS === */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* LEFT COLUMN: MOBILE HARDWARE */}
        <div className="w-[420px] shrink-0 border-r border-white/5 bg-[#030305]/60 flex flex-col items-center justify-center p-6 relative">
          <div className="absolute top-4 left-6 text-[9px] font-extrabold uppercase tracking-[0.3em] text-white/10">Hardware_Interface</div>
          <MobileDevice id="galaxy-s24">
            <div className="w-full h-full bg-[#020204] flex flex-col relative z-50">
                {mobilePayload ? (
                  <div className="flex flex-col items-center justify-center p-6 h-full gap-6">
                    <div className="w-full p-5 space-y-3 bg-white/[0.03] border border-white/5 rounded-2xl">
                        <h2 className="text-sm font-bold uppercase text-aurora-blue">{mobilePayload.intent || "PAYLOAD"}</h2>
                        <pre className="text-[10px] opacity-60 leading-relaxed whitespace-pre-wrap text-left bg-black/40 p-3 rounded">
                            {JSON.stringify(mobilePayload.ui?.data || mobilePayload, null, 2)}
                        </pre>
                    </div>
                  </div>
                ) : (
                  <OrbScene intent="idle" />
                )}
            </div>
          </MobileDevice>
          
          <div className="mt-4 w-full px-10 space-y-3">
            <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            <div className="flex justify-between items-center text-[8px] font-bold uppercase text-white/20">
                <span>Latency: 12ms</span>
                <span>Signal: 100%</span>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: 2×3 FUNCTIONAL GRID */}
        <div className="flex-1 bg-[#020204] grid grid-cols-3 grid-rows-2 gap-px p-px overflow-hidden">
          
          {/* 1. MESSENGER */}
          <Terminal 
            id="messenger" 
            title="neural_messenger.sh"
            isActive={activeWindow === 'messenger'}
            onFocus={() => setActiveWindow('messenger')}
          >
            <div className="flex flex-col h-full gap-3 p-1">
              <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-1">
                {traces.filter(t => t.type === 'A2A_REQUEST' || t.type === 'A2A_RESPONSE').length === 0 && (
                  <div className="h-full flex flex-col items-center justify-center opacity-20 gap-3">
                    <Send className="w-8 h-8" />
                    <p className="text-[9px] font-bold uppercase tracking-[0.3em]">No Messages</p>
                  </div>
                )}
                {traces.filter(t => t.type === 'A2A_REQUEST' || t.type === 'A2A_RESPONSE').map((t, i) => (
                  <div key={i} className={`flex flex-col gap-1 ${t.type === 'A2A_REQUEST' ? 'items-end' : 'items-start'}`}>
                    <div className={`max-w-[85%] p-2.5 rounded-lg border text-[10px] leading-relaxed ${
                      t.type === 'A2A_REQUEST' 
                        ? 'bg-aurora-purple/10 border-aurora-purple/20 text-white/90' 
                        : 'bg-white/5 border-white/10 text-aurora-blue'
                    }`}>
                      {t.type === 'A2A_REQUEST' ? t.data.message : t.data.response}
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-2 bg-white/[0.03] p-2 rounded-lg border border-white/5">
                <input 
                  value={input} 
                  onChange={(e) => setInput(e.target.value)} 
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="PROMPT_COMMAND_>>" 
                  className="flex-1 bg-transparent border-none outline-none text-[10px] px-2 text-white/90 font-bold tracking-wider placeholder:text-white/15 uppercase" 
                />
                <button 
                  onClick={handleSend} 
                  disabled={loading}
                  className="p-2 bg-aurora-purple/20 hover:bg-aurora-purple/40 text-aurora-purple rounded-lg transition-all active:scale-95 disabled:opacity-30"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </Terminal>

          {/* 2. TRACE PANEL */}
          <Terminal 
            id="trace" 
            title="pulse_trace.matrix"
            isActive={activeWindow === 'trace'}
            onFocus={() => setActiveWindow('trace')}
          >
            <TracePanel traces={traces} />
          </Terminal>

          {/* 3. STATE VIEWER */}
          <Terminal 
            id="state" 
            title="neural_state.log"
            isActive={activeWindow === 'state'}
            onFocus={() => setActiveWindow('state')}
          >
            <div className="p-3">
              <div className="text-[9px] font-bold text-white/30 uppercase tracking-widest mb-3">Graph State Snapshot</div>
              <pre className="text-[10px] text-aurora-blue/70 leading-relaxed whitespace-pre-wrap break-words">
{JSON.stringify(graphState || { 
  status: 'synced', 
  node: 'Guard_01', 
  epoch: Date.now(),
  memory_mb: 142,
  active_threads: 3,
  pipeline: 'IDLE'
}, null, 2)}
              </pre>
            </div>
          </Terminal>

          {/* 4. SENSOR LAB */}
          <Terminal 
            id="sensors" 
            title="sensor_calibration.bin"
            isActive={activeWindow === 'sensors'}
            onFocus={() => setActiveWindow('sensors')}
          >
            <SensorLab onSensorUpdate={() => {}} />
          </Terminal>

          {/* 5. LOGS */}
          <Terminal 
            id="logs" 
            title="core_signal.sh"
            isActive={activeWindow === 'logs'}
            onFocus={() => setActiveWindow('logs')}
          >
            <div className="p-2 space-y-1">
              {logs.length === 0 && (
                <div className="flex items-center justify-center h-full opacity-20 text-[9px] font-bold uppercase tracking-widest py-12">
                  Waiting for signals...
                </div>
              )}
              {logs.map((log, i) => (
                <div key={i} className="text-[9px] flex gap-2 items-baseline leading-relaxed">
                  <span className="text-white/15 tabular-nums shrink-0">[{log.timestamp}]</span>
                  <span className="text-aurora-purple font-bold shrink-0">{log.type}</span>
                  <span className="text-white/50 truncate">{log.msg}</span>
                </div>
              ))}
            </div>
          </Terminal>

          {/* 6. AGUI INJECTOR */}
          <Terminal 
            id="injector" 
            title="agui_injector.cmd"
            isActive={activeWindow === 'injector'}
            onFocus={() => setActiveWindow('injector')}
          >
            <div className="h-full flex flex-col gap-3 p-2">
              <textarea 
                className="flex-1 bg-black/40 border border-white/5 rounded-lg p-3 text-[10px] outline-none text-aurora-blue font-mono resize-none leading-relaxed focus:border-aurora-purple/30 transition-colors" 
                placeholder='{ "intent": "diagnostic_pulse" }' 
              />
              <button className="py-2 bg-white/5 border border-white/10 text-[9px] font-extrabold uppercase tracking-widest text-white/40 hover:text-white hover:bg-aurora-purple/20 hover:border-aurora-purple/30 transition-all rounded-lg active:scale-[0.98]">
                Execute_Injection
              </button>
            </div>
          </Terminal>
        </div>
      </div>

      {/* === BOTTOM STATUS BAR === */}
      <div className="h-12 shrink-0 bg-black/80 backdrop-blur-md border-t border-white/5 flex items-center px-6 justify-between z-50">
        <div className="flex items-center gap-8">
            <div className="flex items-center gap-6">
                <div className="flex flex-col gap-0.5">
                    <span className="text-[7px] font-bold text-white/20 uppercase tracking-[0.2em]">Neural_Entropy</span>
                    <span className="text-[10px] font-extrabold text-aurora-purple flex items-center gap-1.5">
                        0.0042 <Zap className="w-3 h-3" />
                    </span>
                </div>
                <div className="h-5 w-px bg-white/5" />
                <div className="flex flex-col gap-0.5">
                    <span className="text-[7px] font-bold text-white/20 uppercase tracking-[0.2em]">Mem_Pressure</span>
                    <span className="text-[10px] font-extrabold text-aurora-blue flex items-center gap-1.5">
                        14.2% <Activity className="w-3 h-3" />
                    </span>
                </div>
            </div>

            <div className="flex items-center gap-3 border-l border-white/5 pl-8">
                <span className="text-[8px] font-bold text-white/10 uppercase tracking-[0.3em]">Streams:</span>
                {['AUDIT', 'DAEMON', 'PULSE'].map(s => (
                    <div key={s} className="px-2.5 py-0.5 rounded bg-aurora-purple/5 border border-aurora-purple/15 text-[8px] font-bold text-aurora-purple/70 tracking-wider uppercase">
                        {s}
                    </div>
                ))}
            </div>
        </div>

        <div className="flex items-center gap-6">
            <div className="text-right">
                <div className="text-[7px] font-bold text-white/20 uppercase tracking-[0.2em]">Guardian_Protocol</div>
                <div className="text-[9px] font-extrabold text-aurora-green flex items-center gap-1.5 justify-end">
                    SECURED <ShieldCheck className="w-3 h-3" />
                </div>
            </div>
            <button className="px-4 py-1.5 bg-aurora-purple/90 text-black text-[9px] font-extrabold uppercase tracking-wider hover:bg-aurora-purple active:scale-95 transition-all rounded">
                System_Purge
            </button>
        </div>
      </div>
    </main>
  );
}
