import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('http://localhost:3005');
  // Wait for the app to initialize
  await page.waitForSelector('text=Neural_Cluster_v2.6');
});

test('Zero Page Scroll Validation', async ({ page }) => {
  // Check if body or html has vertical scroll
  const scrollHeight = await page.evaluate(() => document.documentElement.scrollHeight);
  const clientHeight = await page.evaluate(() => document.documentElement.clientHeight);
  
  // They should be equal (no overflow)
  expect(scrollHeight).toBe(clientHeight);
});

test('Master Puzzle Layout - Edge-to-Edge Alignment', async ({ page }) => {
  // Wait for initial tile
  await page.waitForTimeout(1000);
  
  const sandbox = page.getByTestId('window-sandbox');
  const messenger = page.getByTestId('window-messenger');
  
  const boxS = await sandbox.boundingBox();
  const boxM = await messenger.boundingBox();
  
  // Exact horizontal fit check
  expect(Math.abs(boxM!.x - (boxS!.x + boxS!.width))).toBeLessThanOrEqual(1);
});

test('Window Interaction - Minimization and Dock', async ({ page }) => {
  const messenger = page.getByTestId('window-messenger');
  
  // Minimize
  const header = page.getByTestId('window-header-messenger');
  const minimizeBtn = header.locator('button').nth(1);
  await minimizeBtn.click();
  
  await expect(messenger).not.toBeVisible();
  
  // Restore
  const dockBtn = page.locator('button:has-text("messenger")');
  await dockBtn.click();
  
  await expect(messenger).toBeVisible();
});
