import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

test.describe('Neural Terminal Cluster: UX & UI Integrity Validation', () => {
  
  const reportDir = path.join(__dirname, '../public/test-results/ux-validation');
  
  test.beforeAll(async () => {
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
  });

  test.beforeEach(async ({ page }) => {
    // Port 3008 is the designated stable port for iteration
    await page.goto('http://localhost:3008');
    await page.waitForLoadState('networkidle');
  });

  test('UI Aesthetic: Terminal Cluster & Monospace Integrity', async ({ page }) => {
    // 1. Verify global terminal aesthetic title
    await expect(page.locator('text=NEURAL_TERMINAL_CLUSTER')).toBeVisible();
    
    // 2. Check for terminal-style window headers (path-style)
    await expect(page.locator('span:has-text("root@neural:~/pulse_matrix.exe")')).toBeVisible();
    await expect(page.locator('span:has-text("root@neural:~/context_state.log")')).toBeVisible();

    // 3. Verify CRT Scanline overlay exists
    const scanline = page.locator('div.absolute.inset-0.pointer-events-none.z-\\[5000\\]');
    await expect(scanline).toBeAttached();

    await page.screenshot({ path: path.join(reportDir, '01-terminal-aesthetic.png'), fullPage: true });
  });

  test('Hardware Simulation: Premium Mobile Chassis', async ({ page }) => {
    // 1. Locate the Mobile Device (should NOT have green tint/terminal effects)
    const chassis = page.locator('div.cursor-grab.bg-zinc-900').filter({ has: page.locator('iframe') });
    await expect(chassis).toBeVisible();

    // 2. Verify Dynamic Island
    await expect(page.locator('div.w-28.h-7.bg-black.rounded-full')).toBeAttached();
    
    const iframe = page.frameLocator('iframe[title="AI Node"]');
    await expect(iframe.locator('body')).toBeAttached();

    await page.screenshot({ path: path.join(reportDir, '02-hardware-chassis.png') });
  });

  test('Sensors: Interactive Calibration & Feedback', async ({ page }) => {
    // 1. Find the Sensor Lab window
    await expect(page.locator('text=sensor_calibration.bin')).toBeVisible();

    // 2. Locate Tilt Sliders
    // Tilt X is usually the 4th slider (0, 1, 2 are accel x,y,z)
    const tiltXSlider = page.locator('input[type="range"]').nth(3); 
    await expect(tiltXSlider).toBeVisible();

    // 3. Move Slider and verify 3D visualizer
    await tiltXSlider.fill('45');
    
    // The visual phone in SensorLab should reflect the tilt
    const visualPhone = page.locator('div.bg-indigo-600\\/40.border-indigo-400\\/50');
    const transform = await visualPhone.getAttribute('style');
    expect(transform).toContain('rotateY(45deg)');

    await page.screenshot({ path: path.join(reportDir, '03-sensor-interaction.png') });
  });

  test('Telemetry: Real-time Signal Processing', async ({ page }) => {
    // 1. Check for live telemetry indicators
    await expect(page.locator('text=UPLINK_SECURE')).toBeVisible();
    
    // 2. Test command injection and trace capture
    const input = page.locator('input[placeholder="SEND NEURAL COMMAND..."]');
    await input.fill('NEURAL_PULSE_TEST');
    await page.keyboard.press('Enter');

    // 3. Verify A2A Trace
    await expect(page.getByText('A2A REQUEST')).toBeVisible({ timeout: 20000 });
    
    await page.screenshot({ path: path.join(reportDir, '04-telemetry-signal.png'), fullPage: true });
  });

  test.afterAll(async () => {
    // Generate a summary report index
    const htmlReport = `
      <html>
        <head><title>UX Validation Report</title><style>body{background:#050505;color:#10b981;font-family:monospace;padding:40px;} img{max-width:800px;border:1px solid #10b981;margin:20px 0;}</style></head>
        <body>
          <h1>NEURAL TERMINAL CLUSTER: UX VALIDATION</h1>
          <div><img src="01-terminal-aesthetic.png" /></div>
          <div><img src="02-hardware-chassis.png" /></div>
          <div><img src="03-sensor-interaction.png" /></div>
          <div><img src="04-telemetry-signal.png" /></div>
        </body>
      </html>
    `;
    fs.writeFileSync(path.join(reportDir, 'index.html'), htmlReport);
  });
});
