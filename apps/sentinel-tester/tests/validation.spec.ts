import { test, expect } from '@playwright/test';

test.describe('Neural Terminal Cluster v6.5 Validation', () => {
  
  test.beforeEach(async ({ page }) => {
    // Port 3014 is the active terminal cluster port
    await page.goto('http://localhost:3014');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('text=NEURAL_TERMINAL_CLUSTER')).toBeVisible({ timeout: 30000 });
  });

  test('Interface: Terminal Window Cluster', async ({ page }) => {
    // Check for terminal windows by their mapped titles in the header
    await expect(page.locator('text=root@neural:~/pulse_matrix.exe')).toBeVisible();
    await expect(page.locator('text=root@neural:~/context_state.log')).toBeVisible();
    
    // Check for the Command Line Prompt
    await expect(page.locator('text=>')).toBeVisible();
    await expect(page.locator('input[placeholder="SEND NEURAL COMMAND..."]')).toBeVisible();
  });

  test('Hardware: Neural Uplink (Mobile Device)', async ({ page }) => {
    // Check for the mobile chassis by its cursor and background classes
    const chassis = page.locator('div.cursor-grab.bg-zinc-900').first();
    await expect(chassis).toBeAttached();
    
    // Check for Dynamic Island
    await expect(page.locator('div.w-28.h-7.bg-black.rounded-full')).toBeAttached();
  });

  test('Telemetry: Data Connectivity', async ({ page }) => {
    // Check status bar using more specific locators
    const statusBar = page.locator('div.h-8.bg-zinc-900');
    await expect(statusBar.getByText('REDIS:')).toBeVisible();
    await expect(statusBar.getByText('CORE:')).toBeVisible();
    
    // Test command injection
    const input = page.locator('input[placeholder="SEND NEURAL COMMAND..."]');
    await input.fill('sys_probe');
    await page.keyboard.press('Enter');

    // Check trace Panel
    await expect(page.getByText('A2A REQUEST')).toBeVisible({ timeout: 15000 });
  });
});
