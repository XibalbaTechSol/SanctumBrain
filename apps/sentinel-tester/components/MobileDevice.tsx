'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Signal, Wifi, Battery, Power, Volume2, VolumeX, Camera } from 'lucide-react';

interface MobileDeviceProps {
  children: React.ReactNode;
  id: string;
}

export default function MobileDevice({ 
  children, 
  id
}: MobileDeviceProps) {
  const [isPowerOn, setIsPowerOn] = useState(true);
  const [volume, setVolume] = useState(75);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    };
    updateTime();
    const t = setInterval(updateTime, 10000);
    return () => clearInterval(t);
  }, []);

  const togglePower = () => setIsPowerOn(!isPowerOn);
  const adjustVolume = (delta: number) => {
    setVolume(prev => Math.min(100, Math.max(0, prev + delta)));
    if (isMuted) setIsMuted(false);
  };

  return (
    <div className="relative group p-4" data-testid={`mobile-device-${id}`}>
      {/* GALAXY S24 ULTRA STYLE CHASSIS */}
      <div 
        className="relative mx-auto bg-[#0a0a0c] rounded-[1.5rem] border-[4px] border-[#1c1c1e] shadow-[0_40px_80px_-20px_rgba(0,0,0,0.8),inset_0_0_2px_rgba(255,255,255,0.1)] ring-1 ring-white/5 overflow-hidden titanium-frame" 
        style={{ width: '380px', height: '800px' }}
      >
        {/* TITANIUM SIDES HIGHLIGHTS */}
        <div className="absolute inset-y-0 left-0 w-[1px] bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        <div className="absolute inset-y-0 right-0 w-[1px] bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        
        {/* DYNAMIC PUNCH HOLE / UNDER-DISPLAY SIM */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 w-4 h-4 bg-black rounded-full z-50 flex items-center justify-center border border-white/5 ring-1 ring-blue-500/10">
          <div className="w-1.5 h-1.5 rounded-full bg-[#050515] shadow-[inset_0_0_2px_rgba(255,255,255,0.4)]" />
        </div>

        {/* AMOLED SCREEN */}
        <div 
          className={`absolute inset-[6px] bg-[#020203] z-10 overflow-hidden rounded-[1.2rem] transition-all duration-1000 ${
            isPowerOn ? 'opacity-100' : 'opacity-0 brightness-0 scale-95'
          }`}
          data-testid="mobile-screen"
        >
          {/* STATUS BAR */}
          <div className="absolute top-0 left-0 w-full h-10 flex items-center justify-between px-8 z-40 text-[10px] font-bold text-white/90 font-mono">
            <span>{currentTime}</span>
            <div className="flex items-center gap-2.5">
              <Signal className="w-3 h-3 text-white/60" />
              <Wifi className="w-3 h-3 text-white/60" />
              <div className="flex items-center gap-1 opacity-80">
                <span>88%</span>
                <Battery className="w-3 h-3 rotate-90" />
              </div>
            </div>
          </div>

          {/* SCREEN CONTENT */}
          <div className="w-full h-full pt-10">
            {children}
          </div>

          {/* REFLECTION OVERLAY */}
          <div className="absolute inset-0 pointer-events-none z-[100] opacity-[0.03] bg-gradient-to-br from-white via-transparent to-transparent" />
        </div>

        {/* PHYSICAL HARDWARE BUTTONS (SIMULATED ON SIDES) */}
        {/* Power */}
        <button 
          onClick={togglePower}
          className="absolute right-0 top-40 w-[3px] h-12 bg-[#2c2c2e] rounded-l border border-white/10 z-[200] hover:bg-aurora-purple transition-colors"
        />
        {/* Volume */}
        <div className="absolute right-0 top-60 w-[3px] h-24 bg-[#2c2c2e] rounded-l border border-white/10 z-[200]">
          <button onClick={() => adjustVolume(10)} className="w-full h-1/2 hover:bg-white/10 rounded-tl transition-colors" />
          <button onClick={() => adjustVolume(-10)} className="w-full h-1/2 hover:bg-white/10 rounded-bl transition-colors" />
        </div>
      </div>
      
      {/* NAVIGATION BAR SIM */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-32 h-1 bg-white/10 rounded-full z-[300] blur-[1px]" />

      {/* HARDWARE OVERLAY INFO */}
      <div className="mt-8 flex flex-col items-center gap-2">
        <div className="px-4 py-1.5 rounded-full border border-white/5 bg-white/[0.02] text-[9px] font-black uppercase tracking-[0.3em] text-white/20 flex items-center gap-3">
          <div className={`w-1.5 h-1.5 rounded-full ${isPowerOn ? 'bg-aurora-green animate-pulse shadow-[0_0_8px_#a3be8c]' : 'bg-aurora-red opacity-30'}`} />
          Sovereign_Device_Node_0x71B
        </div>
      </div>
    </div>
  );
}
