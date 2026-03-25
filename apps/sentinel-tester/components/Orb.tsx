'use client';

import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface OrbProps {
  intent?: string;
  isListening?: boolean;
}

export default function Orb({ intent = 'idle', isListening = false }: OrbProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uIntensity: { value: 0.3 },
      uColor1: { value: new THREE.Color('#4f46e5') }, // Default Indigo
      uColor2: { value: new THREE.Color('#ec4899') }, // Default Pink
      uAudioLevel: { value: 0 },
      uPulseSpeed: { value: 0.05 },
      uChaosFactor: { value: 0.0 },
    }),
    []
  );

  useFrame((state) => {
    if (!meshRef.current || !materialRef.current) return;

    const { clock } = state;
    materialRef.current.uniforms.uTime.value = clock.getElapsedTime();

    let color1 = new THREE.Color('#4f46e5'); // Default Indigo
    let color2 = new THREE.Color('#ec4899'); // Default Pink
    let intensity = 0.3;
    let pulseSpeed = 0.05;
    let chaosFactor = 0.0;

    switch (intent.toLowerCase()) {
      case 'listening':
        color1.set('#ec4899'); // Pink
        color2.set('#4f46e5');
        intensity = 0.6;
        pulseSpeed = 0.2;
        break;
      case 'processing':
        color1.set('#6a5acd'); // Violet
        color2.set('#9370db');
        intensity = 0.5;
        pulseSpeed = 0.4;
        break;
      case 'error':
      case 'security_violation':
        color1.set('#FF0000'); // Red
        color2.set('#8B0000');
        intensity = 0.8;
        pulseSpeed = 1.0;
        chaosFactor = 1.0;
        break;
      case 'idle':
      default:
        color1.set('#3b82f6'); // Blueish
        color2.set('#8b5cf6'); // Purpleish
        intensity = 0.4;
        pulseSpeed = 0.1;
        break;
    }

    materialRef.current.uniforms.uColor1.value.lerp(color1, 0.1);
    materialRef.current.uniforms.uColor2.value.lerp(color2, 0.1);
    materialRef.current.uniforms.uIntensity.value = intensity;
    materialRef.current.uniforms.uPulseSpeed.value = pulseSpeed;
    materialRef.current.uniforms.uChaosFactor.value = chaosFactor;
    
    // Scale animation
    meshRef.current.scale.setScalar(1 + Math.sin(clock.getElapsedTime() * pulseSpeed * 20) * 0.05);
  });

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[1, 64]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={`
          uniform float uTime;
          uniform float uAudioLevel;
          uniform float uPulseSpeed;
          uniform float uChaosFactor;
          varying vec2 vUv;
          varying float vDisplacement;
          
          vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
          vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
          vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
          vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
          float snoise(vec3 v) {
            const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
            const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
            
            vec3 i  = floor(v + dot(v, C.yyy) );
            vec3 x0 = v - i + dot(i, C.xxx) ;
            
            vec3 g = step(x0.yzx, x0.xyz);
            vec3 l = 1.0 - g;
            vec3 i1 = min( g.xyz, l.zxy );
            vec3 i2 = max( g.xyz, l.zxy );
            
            vec3 x1 = x0 - i1 + C.xxx;
            vec3 x2 = x0 - i2 + C.yyy;
            vec3 x3 = x0 - D.yyy;
            
            i = mod289(i); 
            vec4 p = permute( permute( permute( 
                       i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
                     + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) 
                     + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
                     
            float n_ = 0.142857142857;
            vec3  ns = n_ * D.wyz - D.xzx;
            
            vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
            
            vec4 x_ = floor(j * ns.z);
            vec4 y_ = floor(j - 7.0 * x_ );
            
            vec4 x = x_ *ns.x + ns.yyyy;
            vec4 y = y_ *ns.x + ns.yyyy;
            vec4 h = 1.0 - abs(x) - abs(y);
            
            vec4 b0 = vec4( x.xy, y.xy );
            vec4 b1 = vec4( x.zw, y.zw );
            
            vec4 s0 = floor(b0)*2.0 + 1.0;
            vec4 s1 = floor(b1)*2.0 + 1.0;
            vec4 sh = -step(h, vec4(0.0));
            
            vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
            vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
            
            vec3 p0 = vec3(a0.xy,h.x);
            vec3 p1 = vec3(a0.zw,h.y);
            vec3 p2 = vec3(a1.xy,h.z);
            vec3 p3 = vec3(a1.zw,h.w);
            
            vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
            p0 *= norm.x;
            p1 *= norm.y;
            p2 *= norm.z;
            p3 *= norm.w;
            
            vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
            m = m * m;
            return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), 
                                          dot(p2,x2), dot(p3,x3) ) );
          }

          void main() {
            vUv = uv;
            vec3 pos = position;
            
            float noise = snoise(pos * 2.0 + uTime * uPulseSpeed);
            if (uChaosFactor > 0.5) {
                noise += snoise(pos * 5.0 + uTime * uChaosFactor * 5.0) * uChaosFactor * 0.5;
            }

            vDisplacement = noise;
            float displacement = noise * (0.2 + uAudioLevel * 0.5 + uPulseSpeed * 0.3);
            pos = pos + normal * displacement;
            
            gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
          }
        `}
        fragmentShader={`
          uniform vec3 uColor1;
          uniform vec3 uColor2;
          uniform float uIntensity;
          varying float vDisplacement;

          void main() {
            vec3 color = mix(uColor1, uColor2, vDisplacement * 2.0 + 0.5);
            float glow = uIntensity * 1.5;
            gl_FragColor = vec4(color * glow, 1.0);
          }
        `}
        uniforms={uniforms}
        transparent
      />
    </mesh>
  );
}
