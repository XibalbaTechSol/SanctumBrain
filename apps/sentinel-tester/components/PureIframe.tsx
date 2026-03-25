'use client';

import React, { useEffect, useRef } from 'react';

interface PureIframeProps {
  html: string;
}

export default function PureIframe({ html }: PureIframeProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (!iframeRef.current) return;

    const standbyHtml = `
      <!DOCTYPE html>
      <html style="height: 100%; width: 100%; margin: 0; padding: 0;">
        <head>
          <script src="https://cdn.tailwindcss.com"></script>
          <style>
            body { 
              margin: 0; 
              padding: 0;
              width: 100%;
              height: 100%;
              background: #000; 
              color: #4f46e5; 
              display: flex; 
              flex-direction: column; 
              align-items: center; 
              justify-content: center; 
              font-family: monospace;
              overflow: hidden;
            }
            .orb { 
              width: 100px; 
              height: 100px; 
              border-radius: 50%; 
              border: 2px solid currentColor; 
              animation: pulse 2s infinite; 
              margin-bottom: 2rem;
              box-shadow: 0 0 40px rgba(79, 70, 229, 0.3);
            }
            @keyframes pulse { 0% { transform: scale(0.9); opacity: 0.2; } 50% { transform: scale(1.1); opacity: 0.7; } 100% { transform: scale(0.9); opacity: 0.2; } }
          </style>
        </head>
        <body>
          <div class="orb"></div>
          <div style="letter-spacing: 0.8em; font-size: 12px; font-weight: 900; opacity: 0.4;">NEURAL STANDBY</div>
        </body>
      </html>
    `;

    // Inject content and ensure attributes are set
    iframeRef.current.srcdoc = html || standbyHtml;
  }, [html]);

  return (
    <div style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'hidden' }}>
      <iframe
        ref={iframeRef}
        title="AI Node"
        sandbox="allow-scripts allow-popups"
        style={{ 
          width: '100%', 
          height: '100%', 
          border: 'none', 
          display: 'block',
          position: 'absolute',
          top: 0,
          left: 0
        }}
      />
    </div>
  );
}
