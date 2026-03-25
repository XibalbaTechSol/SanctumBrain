import { test, expect } from '@playwright/test';

test.describe('Sentinel V3: Redesign & Simulation Validation', () => {
    test.beforeEach(async ({ page }) => {
        // Assume the tester is running on localhost:3005
        await page.goto('http://localhost:3005');
        // Give it a moment to mount
        await page.waitForTimeout(2000);
    });

    test('should render the three-column layout correctly', async ({ page }) => {
        // Column 1: Mobile Hardware Interface Rack
        await expect(page.getByText('Hardware_Interface_Rack')).toBeVisible();
        await expect(page.locator('[data-testid^="mobile-device-"]')).toBeVisible();

        // Column 2: 4x4 Grid of Terminals
        const terminals = page.locator('[data-testid^="terminal-"]');
        const terminalCount = await terminals.count();
        expect(terminalCount).toBe(16);

        // Column 3: Fixed Bottom Panel
        await expect(page.getByText('Neural_Entropy')).toBeVisible();
        await expect(page.getByText('Guardian_Protocol')).toBeVisible();
        await expect(page.getByRole('button', { name: 'System_Purge' })).toBeVisible();
    });

    test('should validate the A2A simulation flow (SLM/VPS)', async ({ page }) => {
        const messenger = page.locator('[data-testid="terminal-messenger"]');
        const input = messenger.locator('input[placeholder="PROMPT_COMMAND_>>"]');
        const sendBtn = messenger.locator('button.bg-aurora-purple\\/20');

        // 1. Send specific diagnostic command that triggers UI
        const testMsg = 'Show me the system health diagnostics and neural entropy report';
        await input.fill(testMsg);
        await sendBtn.click();

        // 2. Wait for simulation results in Trace Matrix
        const trace = page.locator('[data-testid="terminal-trace"]');
        
        // Use a longer timeout for LLM generation
        const waitOptions = { timeout: 30000 };
        
        await expect(trace.locator('[data-testid="trace-item-A2A_REQUEST"]')).toBeVisible(waitOptions);
        await expect(trace.locator('[data-testid="trace-item-SLM_PII_CHECK"]')).toBeVisible(waitOptions);
        await expect(trace.locator('[data-testid="trace-item-VPS_ORCHESTRATOR"]')).toBeVisible(waitOptions);
        await expect(trace.locator('[data-testid="trace-item-A2A_RESPONSE"]')).toBeVisible(waitOptions);
        
        // This is the critical part that confirms UI injection
        await expect(trace.locator('[data-testid="trace-item-AGUI_PAYLOAD"]')).toBeVisible(waitOptions);

        // 3. Verify mobile iframe updates
        const mobileIframe = page.frameLocator('iframe[title="Mobile View"]');
        // Wait for the h2 (Intent) to appear in the iframe
        await expect(mobileIframe.locator('h2')).toBeVisible(waitOptions);
    });

    test('should verify terminal interactivity and snapping', async ({ page }) => {
        const messenger = page.locator('[data-testid="terminal-messenger"]');
        const trace = page.locator('[data-testid="terminal-trace"]');

        await messenger.click();
        await expect(messenger).toHaveClass(/border-aurora-purple/);
        
        await trace.click();
        await expect(trace).toHaveClass(/border-aurora-purple/);
        await expect(messenger).not.toHaveClass(/border-aurora-purple/);

        // Final screenshot of the successful state
        await page.screenshot({ path: 'test-results/sentinel_v3_final_ui.png', fullPage: true });
    });
});
