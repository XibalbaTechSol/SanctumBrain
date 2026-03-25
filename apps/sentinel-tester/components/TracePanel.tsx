'use client';

import React from 'react';
import { Terminal, Database, Activity, Code, Cpu, ShieldCheck } from 'lucide-react';

export interface TraceEvent {
  id: string;
  type: 'A2A_REQUEST' | 'A2A_RESPONSE' | 'AGUI_PAYLOAD' | 'LLM_CODE' | 'RENDER_STATUS' | 'SLM_PII_CHECK' | 'VPS_ORCHESTRATOR';
  data: any;
  timestamp: number;
}

export default function TracePanel({ traces }: { traces: TraceEvent[] }) {
  return (
    <div className="flex flex-col h-full bg-[#050507] overflow-hidden font-mono">
      <div className="p-4 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-aurora-blue/10 rounded-lg border border-aurora-blue/20">
            <Activity className="w-4 h-4 text-aurora-blue animate-pulse" />
          </div>
          <h2 className="text-[10px] font-black tracking-[0.3em] uppercase text-foreground italic skew-x-[-2deg]">Neural_Trace_Matrix</h2>
        </div>
        <div className="flex items-center gap-2 px-2 py-0.5 bg-black/40 rounded border border-white/5">
            <div className="w-1 h-1 rounded-full bg-aurora-green animate-ping" />
            <span className="text-[8px] font-bold text-white/40 tracking-widest">LIVE_STREAM</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {traces.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center opacity-20 gap-4">
            <div className="p-6 bg-white/[0.02] rounded-[2rem] border border-dashed border-white/10">
                <Cpu className="w-12 h-12" />
            </div>
            <p className="text-[10px] font-black uppercase tracking-[0.5em]">Listening_For_Signals</p>
          </div>
        )}

        {traces.map((trace) => (
          <div key={trace.id} className="group relative" data-testid={`trace-item-${trace.type}`}>
            <div className="flex items-center gap-3 mb-2">
              <span className={`w-1.5 h-1.5 rounded-full ${
                trace.type.includes('ERROR') ? 'bg-aurora-red shadow-[0_0_8px_#bf616a]' : 'bg-aurora-green shadow-[0_0_8px_#a3be8c]'
              }`} />
              <span className="text-[9px] font-black text-white/20 tracking-tighter">
                [{new Date(trace.timestamp).toLocaleTimeString([], { hour12: false })}]
              </span>
              <span className={`text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded border ${
                trace.type === 'A2A_REQUEST' ? 'bg-aurora-purple/10 border-aurora-purple/20 text-aurora-purple' :
                trace.type === 'A2A_RESPONSE' ? 'bg-aurora-blue/10 border-aurora-blue/20 text-aurora-blue' :
                'bg-white/5 border-white/10 text-white/40'
              }`}>
                {trace.type.replace(/_/g, ' ')}
              </span>
            </div>
            
            <div className="ml-4 p-4 bg-black/40 rounded-2xl border border-white/5 overflow-x-auto text-[11px] leading-relaxed text-foreground/80 shadow-inner group-hover:border-white/10 transition-colors italic">
              <pre data-testid={`trace-content-${trace.type}`}>
                {typeof trace.data === 'string' ? trace.data : JSON.stringify(trace.data, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-white/5 bg-black/20 flex items-center justify-between text-[9px] font-black uppercase tracking-widest text-white/20">
        <span className="flex items-center gap-2 italic">
          <ShieldCheck className="w-3.5 h-3.5 text-aurora-green/40" />
          Neural_Audit_Complete
        </span>
        <span className="opacity-40">Matrix_Orchestrator_v1.2.4</span>
      </div>
    </div>
  );
}
