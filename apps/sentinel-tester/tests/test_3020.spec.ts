import { test, expect } from '@playwright/test';

test('Phase 4 Sentinel A2A Integation', async ({ page }) => {
  await page.goto('http://localhost:3020/');
  
  // Wait for loading to finish
  await page.waitForTimeout(1000);
  
  // Input trigger
  // Looking at page.tsx, the input is:
  // placeholder="PROMPT_COMMAND_>>"
  const input = page.locator('input[placeholder="PROMPT_COMMAND_>>"]');
  await input.fill('Initiate backend intent test');
  await page.keyboard.press('Enter');
  
  // Wait for response tracing
  // It should appear in the trace list or terminal
  // the right side has a class "bg-aurora-purple/10" or similar
  await page.waitForTimeout(4000); // hard wait to let LLM respond
  
  // Capture success state screenshot specifically into apps/web/public/test-results/
  const fs = require('fs');
  const dir = '/home/xibalba/Projects/SanctumBrain/apps/web/public/test-results';
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  await page.screenshot({ path: `${dir}/success_state.png`, fullPage: true });
});
