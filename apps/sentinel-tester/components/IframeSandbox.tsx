'use client';

import React, { useEffect, useRef } from 'react';
import { Cpu } from 'lucide-react';

interface IframeSandboxProps {
  code: string;
  payload?: any;
}

export default function IframeSandbox({ code, payload }: IframeSandboxProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (!iframeRef.current) return;

    const defaultStandby = `
      (props) => {
        return (
          <div className="flex flex-col items-center justify-center min-h-screen w-full bg-[#050505] text-indigo-500/30 p-8 text-center">
            <div className="relative mb-8">
              <div className="absolute inset-0 bg-indigo-500/10 blur-3xl rounded-full animate-pulse" />
              <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="relative opacity-20">
                <rect x="4" y="4" width="16" height="16" rx="2" />
                <rect x="8" y="8" width="8" height="8" rx="1" />
                <path d="M12 20v2M12 2v2M17 20v2M17 2v2M2 12h2M2 17h2M2 7h2M20 12h2M20 17h2M20 7h2M7 20v2M7 2v2" />
              </svg>
            </div>
            <h2 className="text-xl font-black tracking-[0.3em] uppercase mb-2">Neural Node Standby</h2>
            <p className="font-mono text-[10px] uppercase tracking-[0.5em] animate-pulse">Awaiting Pulse Signal...</p>
          </div>
        );
      }
    `;

    const cleanCode = (code && code.trim()) ? code.replace(/```jsx?|```/g, '').trim() : defaultStandby;

    const srcDoc = `
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8">
          <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
          <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
          <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
          <script src="https://cdn.tailwindcss.com"></script>
          <script src="https://unpkg.com/lucide@latest"></script>
          <style>
            html, body { 
              margin: 0; 
              padding: 0;
              width: 100%;
              height: 100%;
              background: #050505; 
              color: white;
              overflow-x: hidden;
              overflow-y: auto;
              font-family: ui-sans-serif, system-ui, sans-serif;
            }
            #root {
              width: 100%;
              min-height: 100%;
              display: flex;
              flex-direction: column;
            }
            .iframe-container { 
              flex: 1;
              width: 100%; 
              display: flex; 
              flex-direction: column;
              align-items: stretch;
              justify-content: flex-start;
            }
          </style>
          <script>
            tailwind.config = {
              theme: {
                extend: {
                  colors: {
                    indigo: {
                      300: '#a5b4fc', 400: '#818cf8', 500: '#6366f1', 600: '#4f46e5', 900: '#312e81',
                    },
                    slate: { 950: '#020617' }
                  }
                }
              }
            }
          </script>
        </head>
        <body>
          <div id="root"></div>
          <script type="text/babel">
            const { useState, useEffect, useMemo } = React;
            
            const motion = new Proxy({}, {
              get: (target, tag) => {
                if (tag === '$$typeof') return undefined;
                return React.forwardRef(({ initial, animate, transition, whileHover, whileTap, exit, variants, ...props }, ref) => {
                  const Tag = tag;
                  return <Tag {...props} ref={ref} />;
                });
              }
            });

            const data_payload = ${JSON.stringify(payload || {})};

            try {
              const GeneratedComponent = ${cleanCode};

              function App() {
                useEffect(() => {
                  if (window.lucide) {
                    try { window.lucide.createIcons(); } catch(e) {}
                  }
                }, []);

                return (
                  <div className="iframe-container">
                    <GeneratedComponent {...data_payload} />
                  </div>
                );
              }

              const root = ReactDOM.createRoot(document.getElementById('root'));
              root.render(<App />);
            } catch (err) {
              document.getElementById('root').innerHTML = \`
                <div style="padding: 2rem; background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.3); border-radius: 1.5rem; color: #f87171; font-family: monospace; margin: 2rem;">
                  <div style="font-weight: bold; margin-bottom: 8px;">RUNTIME ERROR</div>
                  <div>\${err.message}</div>
                </div>
              \`;
            }
          </script>
        </body>
      </html>
    `;

    iframeRef.current.srcdoc = srcDoc;
  }, [code, payload]);

  return (
    <div className="absolute inset-0 w-full h-full bg-[#050505]">
      <iframe
        ref={iframeRef}
        className="w-full h-full border-none block"
        title="Generative UI Sandbox"
        sandbox="allow-scripts allow-modals"
      />
    </div>
  );
}
