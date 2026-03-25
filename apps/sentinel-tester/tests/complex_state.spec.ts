import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test.describe('Neural Sentinel: Complex State Validation', () => {
  
  const reportDir = path.join(__dirname, '../public/test-results/complex-audit');
  
  test.beforeAll(async () => {
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
  });

  test('should execute full multi-step security audit and node deployment', async ({ page }) => {
    // Set a very long timeout for the whole test
    test.setTimeout(120000);

    // 1. Initialize
    await page.goto('http://localhost:3005');
    await expect(page.locator('h1:has-text("Sentinel Core")')).toBeVisible({ timeout: 20000 });
    await page.screenshot({ path: path.join(reportDir, '01-initialized.png') });

    // 2. Inject Intent
    const input = page.locator('input[placeholder="Inject Neural Intent..."]');
    await input.fill('Perform a deep security audit and initialize aggressive node deployment');
    await page.locator('button:has(svg.lucide-send)').click();

    // 3. Wait for A2A Response signal in Trace Panel
    console.log('[TEST] Waiting for A2A response...');
    await expect(page.locator('text=A2A RESPONSE')).toBeVisible({ timeout: 60000 });
    await page.screenshot({ path: path.join(reportDir, '02-a2a-received.png') });

    // 4. Wait for AGUI Payload
    console.log('[TEST] Waiting for AGUI payload...');
    await expect(page.locator('text=AGUI PAYLOAD')).toBeVisible({ timeout: 20000 });

    // 5. Wait for the AI generated UI to stabilize in the iframe
    const iframe = page.frameLocator('iframe[title="AI Node"]');
    console.log('[TEST] Waiting for AI content to mount...');
    
    // Fallback or Live UI should have some buttons
    const anyBtn = iframe.locator('button').first();
    await expect(anyBtn).toBeVisible({ timeout: 30000 });
    await page.screenshot({ path: path.join(reportDir, '03-ui-ready.png'), fullPage: true });

    // 6. Interaction Step 1: Scan
    const scanBtn = iframe.locator('button:has-text("Scan"), button:has-text("Initialize"), #scan-btn').first();
    console.log('[TEST] Clicking Scan/Initialize...');
    await scanBtn.click();
    
    // Wait for progress or status change (fallback takes 2s)
    await page.waitForTimeout(4000); 
    await page.screenshot({ path: path.join(reportDir, '04-scanning.png') });

    // 7. Interaction Step 2: Protocol Selection
    const aggressiveBtn = iframe.locator('button:has-text("AGGRESSIVE"), #protocol-aggressive').first();
    if (await aggressiveBtn.isVisible()) {
      console.log('[TEST] Setting AGGRESSIVE protocol...');
      await aggressiveBtn.click();
      await page.waitForTimeout(1000);
    }

    // 8. Interaction Step 3: Global Deployment
    const deployBtn = iframe.locator('button:has-text("Deploy"), button:has-text("Execute"), #deploy-btn').first();
    console.log('[TEST] Deploying...');
    await expect(deployBtn).toBeEnabled({ timeout: 10000 });
    await deployBtn.click();

    // 9. Interaction Step 4: Confirm
    const confirmBtn = iframe.locator('button:has-text("Confirm"), button:has-text("Yes"), #confirm-btn').first();
    if (await confirmBtn.isVisible()) {
      console.log('[TEST] Confirming...');
      await confirmBtn.click();
      await page.waitForTimeout(2000);
    }

    // 10. Final State Validation
    // Fixed multi-selector syntax
    const finalState = iframe.locator('h1:has-text("SECURE"), :text("SUCCESS"), :text("LOCKED"), :text("successful")').first();
    await expect(finalState).toBeVisible({ timeout: 15000 });
    
    await page.screenshot({ path: path.join(reportDir, '06-success.png'), fullPage: true });
    console.log('[PLAYWRIGHT] Complex Interaction Suite Passed.');
  });
});
