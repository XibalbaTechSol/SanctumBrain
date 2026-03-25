import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('http://localhost:3005');
  // Wait for the app to initialize
  await page.waitForSelector('text=Sanctum_Diagnostics');
});

test('Linux Terminal Aesthetic and Window Controls', async ({ page }) => {
  const traceWindow = page.getByTestId('window-trace');
  await expect(traceWindow).toBeVisible();
  
  // Check for Linux traffic light dots
  const closeBtn = page.getByTestId('window-close-trace');
  await expect(closeBtn).toBeVisible();
  
  // Check for title style
  await expect(page.locator('text=Pulse_Matrix_Stream.exe')).toBeVisible();
});

test('Galaxy Simulator Hardware Interaction', async ({ page }) => {
  const powerBtn = page.getByTestId('mobile-power-btn');
  const screen = page.getByTestId('mobile-screen');
  
  // Initially screen should be visible
  await expect(screen).toBeVisible();
  
  // Click hardware power button
  await powerBtn.click();
  
  // Screen should have opacity-0 class (amoled off simulation)
  await expect(screen).toHaveClass(/opacity-0/);
  
  // Power back on
  await powerBtn.click();
  await expect(screen).toHaveClass(/opacity-100/);
});

test('Reorganizable Windows (Dragging)', async ({ page }) => {
  const traceHeader = page.getByTestId('window-header-trace');
  const initialBox = await traceHeader.boundingBox();
  
  if (initialBox) {
    const centerX = initialBox.x + initialBox.width / 2;
    const centerY = initialBox.y + initialBox.height / 2;
    
    await page.mouse.move(centerX, centerY);
    await page.mouse.down();
    // Move slowly to ensure drag triggers
    await page.mouse.move(centerX + 100, centerY + 50, { steps: 10 });
    await page.mouse.up();
    
    const newBox = await traceHeader.boundingBox();
    expect(newBox!.x).toBeGreaterThan(initialBox.x);
  }
});

test('End-to-End Neural Orchestration Simulation', async ({ page }) => {
  const input = page.locator('input[placeholder*="Execute Neural Command"]');
  await input.fill('Simulate system breach detection');
  await page.keyboard.press('Enter');

  // Verify Traces appear using test-ids
  await expect(page.getByTestId('trace-item-A2A_REQUEST')).toBeVisible({ timeout: 10000 });
  await expect(page.getByTestId('trace-item-SLM_PII_CHECK')).toBeVisible({ timeout: 15000 });
  await expect(page.getByTestId('trace-item-VPS_ORCHESTRATOR')).toBeVisible();
  await expect(page.getByTestId('trace-item-A2A_RESPONSE')).toBeVisible();
  
  // Verify trace content
  const responseContent = page.getByTestId('trace-content-A2A_RESPONSE');
  await expect(responseContent).toContainText(/Neural/i);
});
