import { test, expect } from '@playwright/test';
import fs from 'fs';

test.describe('E2E A2A Flow Validation', () => {
    test.setTimeout(60000);

    test('should validate message sending, SLM intent inference, VPS communication, and dynamic UI rendering', async ({ page }) => {
        // Using localhost:3020 as seen in the active browser session
        await page.goto('http://localhost:3020');
        await page.waitForTimeout(2000); // Give it a moment to mount and connect

        // 1. Locate the messenger terminal input
        const messengerTitle = page.locator('text=neural_messenger.sh');
        await expect(messengerTitle).toBeVisible();
        const input = page.locator('input[placeholder="PROMPT_COMMAND_>>"]');
        const sendBtn = page.locator('button:has(svg.lucide-send)');

        // 2. Send the message
        const testMsg = 'Check system health and render the diagnostic payload';
        await input.fill(testMsg);
        await sendBtn.click();

        // 3. Verify Trace Panel for the lifecycle
        // Trace panel items have data-testid attributes
        const waitOptions = { timeout: 45000 };
        
        // Wait for the local A2A_REQUEST trace
        await expect(page.locator('[data-testid="trace-item-A2A_REQUEST"]')).toBeVisible(waitOptions);
        
        // Wait for backend communication trace steps
        await expect(page.locator('[data-testid="trace-item-SLM_PII_CHECK"]')).toBeVisible(waitOptions);
        await expect(page.locator('[data-testid="trace-item-VPS_ORCHESTRATOR"]')).toBeVisible(waitOptions);
        await expect(page.locator('[data-testid="trace-item-A2A_RESPONSE"]')).toBeVisible(waitOptions);
        await expect(page.locator('[data-testid="trace-item-AGUI_PAYLOAD"]')).toBeVisible(waitOptions);

        // 4. Verify Mobile Device Payload Rendering
        // The mobile interface renders an H2 with the intent which should be visible after rendering
        // In the app/page.tsx, it renders <h2 className="text-sm font-bold uppercase text-aurora-blue">{mobilePayload.intent || "PAYLOAD"}</h2>
        const mobileContainer = page.locator('h2.text-aurora-blue');
        await expect(mobileContainer).toBeVisible(waitOptions);

        // Capture screenshot of successful state
        const screenshotPath = 'public/test-results/a2a_flow_success.png';
        await page.screenshot({ path: screenshotPath, fullPage: true });
        
        expect(fs.existsSync(screenshotPath)).toBeTruthy();
    });
});
