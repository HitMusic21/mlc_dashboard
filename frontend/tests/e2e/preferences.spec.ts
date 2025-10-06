/**
 * User Preferences Tests
 *
 * Tests theme switching, items per page, and dashboard layout customization.
 */

import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'admin@example.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/');
});

test.describe('User Preferences', () => {
  test('should open preferences modal', async ({ page }) => {
    await page.click('.user-button');
    await page.click('text=Preferences');

    await expect(page.locator('.preferences-modal, .modal')).toBeVisible();
    await expect(page.locator('text=Theme')).toBeVisible();
  });

  test('should switch theme to dark', async ({ page }) => {
    // Open preferences
    await page.click('.user-button');
    await page.click('text=Preferences');

    // Select dark theme
    await page.click('.preferences-modal__theme-option:has-text("Dark")');

    // Save changes
    await page.click('button:has-text("Save")');

    // Check dark theme is applied
    const html = page.locator('html');
    await expect(html).toHaveAttribute('data-theme', 'dark');
  });

  test('should switch theme to light', async ({ page }) => {
    // First set to dark
    await page.click('.user-button');
    await page.click('text=Preferences');
    await page.click('.preferences-modal__theme-option:has-text("Dark")');
    await page.click('button:has-text("Save")');

    // Then switch to light
    await page.click('.user-button');
    await page.click('text=Preferences');
    await page.click('.preferences-modal__theme-option:has-text("Light")');
    await page.click('button:has-text("Save")');

    // Check light theme is applied
    const html = page.locator('html');
    await expect(html).toHaveAttribute('data-theme', 'light');
  });

  test('should change items per page', async ({ page }) => {
    // Open preferences
    await page.click('.user-button');
    await page.click('text=Preferences');

    // Change items per page
    await page.selectOption('.preferences-modal__select, select', '100');

    // Save changes
    await page.click('button:has-text("Save")');

    // Preference should be saved (could verify by checking a table pagination)
    await expect(page.locator('.preferences-modal')).not.toBeVisible();
  });

  test('should cancel preference changes', async ({ page }) => {
    // Get current theme
    const htmlBefore = await page.locator('html').getAttribute('data-theme');

    // Open preferences and make changes
    await page.click('.user-button');
    await page.click('text=Preferences');
    await page.click('.preferences-modal__theme-option:has-text("Dark")');

    // Cancel instead of save
    await page.click('button:has-text("Cancel")');

    // Theme should not change
    const htmlAfter = await page.locator('html').getAttribute('data-theme');
    expect(htmlAfter).toBe(htmlBefore);
  });

  test('should persist theme across page reload', async ({ page }) => {
    // Set dark theme
    await page.click('.user-button');
    await page.click('text=Preferences');
    await page.click('.preferences-modal__theme-option:has-text("Dark")');
    await page.click('button:has-text("Save")');

    // Reload page
    await page.reload();

    // Dark theme should persist
    const html = page.locator('html');
    await expect(html).toHaveAttribute('data-theme', 'dark');
  });
});

test.describe('Dashboard Layout Editor', () => {
  test('should open layout editor', async ({ page }) => {
    await page.click('.user-button');
    await page.click('text=Dashboard Layout');

    await expect(page.locator('.layout-editor, .modal')).toBeVisible();
  });

  test('should display available widgets', async ({ page }) => {
    await page.click('.user-button');
    await page.click('text=Dashboard Layout');

    // Check for widget palette
    await expect(page.locator('text=Available Widgets')).toBeVisible();
    await expect(page.locator('text=Statistics Cards')).toBeVisible();
    await expect(page.locator('text=Charts Panel')).toBeVisible();
  });

  test('should add a widget', async ({ page }) => {
    await page.click('.user-button');
    await page.click('text=Dashboard Layout');

    // Get current widget count
    const widgetsBefore = await page.locator('.layout-editor__widget-item').count();

    // Add a widget
    await page.click('.layout-editor__widget-palette-item:has-text("Notifications")');

    // Widget count should increase
    const widgetsAfter = await page.locator('.layout-editor__widget-item').count();
    expect(widgetsAfter).toBe(widgetsBefore + 1);
  });

  test('should remove a widget', async ({ page }) => {
    await page.click('.user-button');
    await page.click('text=Dashboard Layout');

    // Wait for widgets to load
    await page.waitForSelector('.layout-editor__widget-item');

    // Get current widget count
    const widgetsBefore = await page.locator('.layout-editor__widget-item').count();

    if (widgetsBefore > 0) {
      // Remove first widget
      await page.locator('.layout-editor__widget-item').first().locator('button[aria-label="Remove widget"]').click();

      // Widget count should decrease
      const widgetsAfter = await page.locator('.layout-editor__widget-item').count();
      expect(widgetsAfter).toBe(widgetsBefore - 1);
    }
  });

  test('should save layout changes', async ({ page }) => {
    await page.click('.user-button');
    await page.click('text=Dashboard Layout');

    // Add a widget
    await page.click('.layout-editor__widget-palette-item:has-text("Notifications")');

    // Save layout
    await page.click('button:has-text("Save Layout")');

    // Modal should close
    await expect(page.locator('.layout-editor')).not.toBeVisible();
  });
});
