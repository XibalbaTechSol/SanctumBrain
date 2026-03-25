'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Terminal as TerminalIcon, X, Minus, Square } from 'lucide-react';

interface TerminalProps {
  title: string;
  children: React.ReactNode;
  id: string;
  isActive?: boolean;
  onFocus?: () => void;
  onClose?: () => void;
}

export default function Terminal({ 
  title, 
  children, 
  id,
  isActive,
  onFocus,
  onClose
}: TerminalProps) {
  return (
    <div 
      onPointerDown={onFocus}
      className={`group flex flex-col bg-[#050507] border h-full w-full transition-all duration-200 overflow-hidden relative ${
        isActive 
          ? 'border-aurora-purple/40 shadow-[0_0_20px_rgba(180,142,173,0.08)] z-10' 
          : 'border-white/[0.06] hover:border-white/10'
      }`}
      data-testid={`terminal-${id}`}
    >
      {/* HEADER */}
      <div className={`h-8 shrink-0 flex items-center justify-between px-3 select-none transition-colors ${
        isActive ? 'bg-aurora-purple/[0.06]' : 'bg-black/40'
      } border-b border-white/[0.06]`}>
        <div className="flex items-center gap-2.5">
          <TerminalIcon className={`w-3 h-3 ${isActive ? 'text-aurora-purple' : 'text-white/15'}`} />
          <span className={`text-[10px] font-mono font-bold tracking-wider ${
            isActive ? 'text-white/80' : 'text-white/30'
          }`}>
            {title}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <button className="p-0.5 hover:bg-white/5 rounded transition-colors">
              <Minus className="w-2.5 h-2.5 text-white/30" />
            </button>
            <button className="p-0.5 hover:bg-white/5 rounded transition-colors">
              <Square className="w-2 h-2 text-white/30" />
            </button>
            <button onClick={(e) => { e.stopPropagation(); onClose?.(); }} className="p-0.5 hover:bg-aurora-red/20 rounded transition-colors">
              <X className="w-2.5 h-2.5 text-aurora-red/50 hover:text-aurora-red" />
            </button>
          </div>
          <div className={`text-[8px] font-mono font-bold ${isActive ? 'text-aurora-purple/60' : 'text-white/10'}`}>
            0x{id.slice(0, 4).toUpperCase()}
          </div>
        </div>
      </div>

      {/* CONTENT AREA */}
      <div className="flex-1 overflow-hidden relative bg-[#020204]">
        <div className="h-full w-full overflow-y-auto custom-scrollbar">
          {children}
        </div>
        
        {/* SCANLINES EFFECT */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.02] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%)] bg-[length:100%_4px]" />
        
        {/* VIGNETTE */}
        <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_30px_rgba(0,0,0,0.3)]" />
      </div>

      {/* ACTIVE GLOW STRIP */}
      {isActive && (
        <motion.div 
          layoutId="active-terminal-indicator"
          className="absolute bottom-0 left-0 right-0 h-[2px] bg-aurora-purple shadow-[0_0_10px_#b48ead]"
        />
      )}
    </div>
  );
}
