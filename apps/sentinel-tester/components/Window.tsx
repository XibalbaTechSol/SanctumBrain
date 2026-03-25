'use client';

import React, { useState, useEffect } from 'react';
import { motion, useDragControls, AnimatePresence } from 'framer-motion';
import { Terminal as TerminalIcon, X, Minus } from 'lucide-react';

interface WindowProps {
  title: string;
  children: React.ReactNode;
  initialX?: number;
  initialY?: number;
  initialWidth?: number;
  initialHeight?: number;
  zIndex: number;
  onFocus: () => void;
  id: string;
  isActive?: boolean;
  onClose?: () => void;
  isMinimized?: boolean;
  onMinimize?: () => void;
}

export default function Window({ 
  title, 
  children, 
  initialX = 100, 
  initialY = 100, 
  initialWidth = 500, 
  initialHeight = 400,
  zIndex,
  onFocus,
  id,
  isActive,
  onClose,
  isMinimized,
  onMinimize
}: WindowProps) {
  const [isMounted, setIsMounted] = useState(false);
  const dragControls = useDragControls();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  return (
    <AnimatePresence mode="wait">
      {!isMinimized && (
        <motion.div
          drag
          dragControls={dragControls}
          dragListener={false}
          dragMomentum={false}
          onPointerDown={onFocus}
          initial={{ x: initialX, y: initialY, width: initialWidth, height: initialHeight, opacity: 0 }}
          animate={{ 
            opacity: 1, 
            x: initialX,
            y: initialY,
            width: initialWidth,
            height: initialHeight
          }}
          exit={{ opacity: 0, scale: 0.99 }}
          transition={{ type: 'spring', damping: 40, stiffness: 600, mass: 0.5 }}
          className={`absolute flex flex-col bg-[#050507] border transition-all duration-200 pointer-events-auto ${isActive ? 'border-aurora-purple z-50 shadow-[0_0_40px_rgba(0,0,0,0.9)]' : 'border-white/5'}`}
          style={{ zIndex, borderRadius: '0px' }}
          data-testid={`window-${id}`}
        >
          {/* FLUSH HEADER */}
          <div 
            onPointerDown={(e) => {
              onFocus();
              dragControls.start(e);
            }}
            className={`h-7 shrink-0 flex items-center justify-between px-2 cursor-grab active:cursor-grabbing select-none transition-colors duration-200 ${isActive ? 'bg-white/[0.05]' : 'bg-black/40'} border-b border-white/5`}
            data-testid={`window-header-${id}`}
          >
            <div className="flex items-center gap-2">
              <div className="flex gap-1.5 mr-1">
                <button 
                  onClick={(e) => { e.stopPropagation(); onClose?.(); }} 
                  className="w-2.5 h-2.5 rounded-full bg-aurora-red/40 hover:bg-aurora-red transition-colors flex items-center justify-center group/btn"
                >
                  <X className="w-1.5 h-1.5 text-black opacity-0 group-hover/btn:opacity-100" />
                </button>
                <button 
                  onClick={(e) => { e.stopPropagation(); onMinimize?.(); }}
                  className="w-2.5 h-2.5 rounded-full bg-aurora-yellow/40 hover:bg-aurora-yellow transition-colors flex items-center justify-center group/btn"
                >
                  <Minus className="w-1.5 h-1.5 text-black opacity-0 group-hover/btn:opacity-100" />
                </button>
              </div>
              
              <span className={`text-[8px] font-black uppercase tracking-[0.3em] font-mono ${isActive ? 'text-foreground' : 'text-white/20'}`}>
                {title}
              </span>
            </div>

            <div className={`text-[7px] font-black tracking-widest ${isActive ? 'text-aurora-purple' : 'text-white/10'}`}>
                0x{id.slice(0,4).toUpperCase()}
            </div>
          </div>

          {/* FLUSH CONTENT AREA */}
          <div className="flex-1 overflow-hidden relative bg-black flex flex-col">
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              {children}
            </div>
            
            {/* Extremely subtle CRT effect */}
            <div className="absolute inset-0 pointer-events-none opacity-[0.01] bg-[linear-gradient(rgba(18,16,16,0) 50%,rgba(0,0,0,0.25) 50%)] bg-[length:100%_2px]" />
          </div>

          {/* ACTIVE INDICATOR FOOTER */}
          {isActive && (
            <motion.div 
                layoutId={`active-footer-${id}`}
                className="h-[1px] bg-aurora-purple shadow-[0_0_10px_#b48ead] shrink-0" 
            />
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
