'use client';

import React from 'react';

interface PhoneFrameProps {
  children: React.ReactNode;
}

export default function PhoneFrame({ children }: PhoneFrameProps) {
  return (
    <div className="relative group">
      {/* OUTER SHADOW & GLOW */}
      <div className="absolute -inset-4 bg-indigo-500/10 rounded-[4rem] blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
      
      {/* THE DEVICE CHASSIS */}
      <div className="relative w-[360px] h-[760px] bg-zinc-900 rounded-[3.5rem] p-[12px] shadow-2xl border border-zinc-800 ring-1 ring-white/5">
        
        {/* INNER SCREEN CONTAINER */}
        <div className="w-full h-full bg-black rounded-[2.8rem] overflow-hidden relative shadow-[inset_0_0_2px_rgba(255,255,255,0.1)]">
          
          {/* DYNAMIC ISLAND */}
          <div className="absolute top-3 left-1/2 -translate-x-1/2 w-28 h-7 bg-black rounded-full z-50 border border-white/5 flex items-center justify-end px-3">
            <div className="w-1.5 h-1.5 rounded-full bg-zinc-900 ring-1 ring-white/10" />
          </div>

          {/* THE ACTUAL CONTENT */}
          <div className="w-full h-full relative z-10">
            {children}
          </div>

          {/* HOME BAR */}
          <div className="absolute bottom-1.5 left-1/2 -translate-x-1/2 w-32 h-1 bg-white/20 rounded-full z-50 backdrop-blur-md" />
        </div>

        {/* PHYSICAL BUTTONS (Minimalist) */}
        <div className="absolute -left-[2px] top-28 w-[3px] h-10 bg-zinc-800 rounded-l-sm" />
        <div className="absolute -left-[2px] top-44 w-[3px] h-16 bg-zinc-800 rounded-l-sm" />
        <div className="absolute -left-[2px] top-64 w-[3px] h-16 bg-zinc-800 rounded-l-sm" />
        <div className="absolute -right-[2px] top-44 w-[3px] h-24 bg-zinc-800 rounded-r-sm" />
      </div>
    </div>
  );
}
