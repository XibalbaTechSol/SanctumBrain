'use client';

import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment } from '@react-three/drei';
import Orb from './Orb';

export default function OrbScene({ intent = 'idle' }: { intent?: string }) {
  return (
    <div className="w-full h-full min-h-[300px] flex items-center justify-center">
      <Canvas dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 0, 4]} fov={50} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate={true} autoRotateSpeed={0.5} />
        
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="purple" />
        
        <Suspense fallback={null}>
            <Orb intent={intent} />
            <Environment preset="city" />
        </Suspense>
      </Canvas>
    </div>
  );
}
