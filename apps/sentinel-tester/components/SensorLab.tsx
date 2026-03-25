'use client';

import React, { useState, useEffect } from 'react';
import { Smartphone, Move, RotateCcw, Activity } from 'lucide-react';

interface SensorData {
  accel: { x: number; y: number; z: number };
  gyro: { alpha: number; beta: number; gamma: number };
  orientation: { tiltX: number; tiltY: number; compass: number };
}

export default function SensorLab({ onSensorUpdate }: { onSensorUpdate: (data: SensorData) => void }) {
  const [sensors, setSensors] = useState<SensorData>({
    accel: { x: 0, y: 0, z: 9.8 },
    gyro: { alpha: 0, beta: 0, gamma: 0 },
    orientation: { tiltX: 0, tiltY: 0, compass: 0 }
  });

  const updateSensor = (category: keyof SensorData, field: string, value: number) => {
    setSensors(prev => {
      const next = {
        ...prev,
        [category]: { ...prev[category], [field]: value }
      };
      onSensorUpdate(next);
      return next;
    });
  };

  const resetSensors = () => {
    const initial = {
      accel: { x: 0, y: 0, z: 9.8 },
      gyro: { alpha: 0, beta: 0, gamma: 0 },
      orientation: { tiltX: 0, tiltY: 0, compass: 0 }
    };
    setSensors(initial);
    onSensorUpdate(initial);
  };

  return (
    <div className="p-4 space-y-6 font-mono text-[10px]">
      
      {/* 3D VISUALIZER */}
      <div className="h-32 bg-black/40 rounded-xl border border-white/5 flex items-center justify-center perspective-[500px]">
        <div 
          className="w-12 h-20 bg-indigo-600/40 border border-indigo-400/50 rounded-md transition-transform duration-100 ease-linear shadow-[0_0_20px_rgba(99,102,241,0.3)]"
          style={{ 
            transform: `rotateX(${sensors.orientation.tiltY}deg) rotateY(${sensors.orientation.tiltX}deg) rotateZ(${sensors.gyro.alpha}deg)` 
          }}
        />
      </div>

      {/* ACCELEROMETER */}
      <section className="space-y-3">
        <div className="flex justify-between items-center text-indigo-400">
          <h3 className="uppercase font-black tracking-widest flex items-center gap-2">
            <Activity className="w-3 h-3" /> Accelerometer (m/s²)
          </h3>
          <button onClick={resetSensors} className="p-1 hover:bg-white/5 rounded text-muted-foreground">
            <RotateCcw className="w-3 h-3" />
          </button>
        </div>
        <div className="space-y-4">
          {Object.entries(sensors.accel).map(([axis, val]) => (
            <div key={axis} className="space-y-1">
              <div className="flex justify-between uppercase opacity-50">
                <span>Axis {axis}</span>
                <span>{val.toFixed(2)}</span>
              </div>
              <input 
                type="range" min="-20" max="20" step="0.1" value={val}
                onChange={(e) => updateSensor('accel', axis, parseFloat(e.target.value))}
                className="w-full accent-indigo-500 h-1 bg-white/5 rounded-full appearance-none cursor-pointer"
              />
            </div>
          ))}
        </div>
      </section>

      {/* ORIENTATION / TILT */}
      <section className="space-y-3">
        <h3 className="uppercase font-black tracking-widest flex items-center gap-2 text-emerald-400">
          <Move className="w-3 h-3" /> Device Tilt (deg)
        </h3>
        <div className="space-y-4">
          <div className="space-y-1">
            <div className="flex justify-between uppercase opacity-50">
              <span>Tilt X (Gamma)</span>
              <span>{sensors.orientation.tiltX}°</span>
            </div>
            <input 
              type="range" min="-90" max="90" value={sensors.orientation.tiltX}
              onChange={(e) => updateSensor('orientation', 'tiltX', parseInt(e.target.value))}
              className="w-full accent-emerald-500 h-1 bg-white/5 rounded-full appearance-none"
            />
          </div>
          <div className="space-y-1">
            <div className="flex justify-between uppercase opacity-50">
              <span>Tilt Y (Beta)</span>
              <span>{sensors.orientation.tiltY}°</span>
            </div>
            <input 
              type="range" min="-90" max="90" value={sensors.orientation.tiltY}
              onChange={(e) => updateSensor('orientation', 'tiltY', parseInt(e.target.value))}
              className="w-full accent-emerald-500 h-1 bg-white/5 rounded-full appearance-none"
            />
          </div>
        </div>
      </section>

      <div className="pt-4 border-t border-white/5 text-center text-[8px] text-muted-foreground uppercase tracking-[0.2em]">
        Dispatching Live Sensor Packet
      </div>
    </div>
  );
}
