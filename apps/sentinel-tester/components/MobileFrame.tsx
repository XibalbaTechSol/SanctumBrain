'use client';

import React from 'react';

interface MobileFrameProps {
  children: React.ReactNode;
}

export default function MobileFrame({ children }: MobileFrameProps) {
  return (
    <div className="relative mx-auto bg-[#080808] rounded-[3.5rem] border-[12px] border-[#1a1a1a] shadow-[0_0_80px_rgba(0,0,0,0.9)] overflow-hidden ring-1 ring-white/10" 
         style={{ width: '380px', height: '800px' }}>
      
      {/* GLOSS REFLECTION */}
      <div className="absolute inset-0 pointer-events-none z-30 opacity-20 bg-gradient-to-tr from-transparent via-white/5 to-transparent" />

      {/* DYNAMIC ISLAND */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 w-32 h-8 bg-black rounded-[2rem] z-40 flex items-center justify-end px-4 border border-white/5">
        <div className="w-2 h-2 rounded-full bg-[#111] border border-indigo-500/20 shadow-[inset_0_0_2px_rgba(99,102,241,0.5)]" />
      </div>

      {/* HARDWARE BUTTONS */}
      <div className="absolute -left-[13px] top-32 w-[3px] h-10 bg-[#222] rounded-l-md shadow-sm" /> {/* Action */}
      <div className="absolute -left-[13px] top-48 w-[3px] h-16 bg-[#222] rounded-l-md shadow-sm" /> {/* Vol Up */}
      <div className="absolute -left-[13px] top-68 w-[3px] h-16 bg-[#222] rounded-l-md shadow-sm" /> {/* Vol Down */}
      <div className="absolute -right-[13px] top-48 w-[3px] h-24 bg-[#222] rounded-r-md shadow-sm" /> {/* Side */}

      {/* ANTENNA BANDS */}
      <div className="absolute left-12 -top-[12px] w-4 h-[3px] bg-[#222]" />
      <div className="absolute right-12 -top-[12px] w-4 h-[3px] bg-[#222]" />
      <div className="absolute left-12 -bottom-[12px] w-4 h-[3px] bg-[#222]" />
      <div className="absolute right-12 -bottom-[12px] w-4 h-[3px] bg-[#222]" />

      {/* THE SCREEN */}
      <div className="w-full h-full bg-black relative z-10 overflow-hidden rounded-[2.8rem]">
        {children}
      </div>

      {/* HOME INDICATOR */}
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-32 h-1.5 bg-white/20 rounded-full z-20 backdrop-blur-md" />
    </div>
  );
}
