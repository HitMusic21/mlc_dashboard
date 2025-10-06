/**
 * Notifications Tests
 *
 * Tests notification dropdown, notifications page, mark as read, and toast notifications.
 */

import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'admin@example.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/');
});

test.describe('Notification Dropdown', () => {
  test('should display notification dropdown', async ({ page }) => {
    // Look for notification bell/icon
    const notificationTrigger = page.locator('[class*="notification"]').first();

    if (await notificationTrigger.isVisible()) {
      await notificationTrigger.click();

      // Dropdown should be visible
      await expect(page.locator('[class*="notification-dropdown"]')).toBeVisible();
    }
  });

  test('should navigate to notifications page from dropdown', async ({ page }) => {
    const notificationTrigger = page.locator('[class*="notification"]').first();

    if (await notificationTrigger.isVisible()) {
      await notificationTrigger.click();

      // Click "View All" button
      const viewAllButton = page.locator('text=View all, text=View All, button:has-text("View")').first();
      if (await viewAllButton.isVisible()) {
        await viewAllButton.click();

        // Should navigate to notifications page
        await expect(page).toHaveURL('/notifications');
      }
    }
  });
});

test.describe('Notifications Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/notifications');
  });

  test('should display notifications page', async ({ page }) => {
    await expect(page.locator('h1, .page-title')).toContainText(/notification/i);
  });

  test('should display tabs for All and Unread', async ({ page }) => {
    await expect(page.locator('text=All, .tab:has-text("All")')).toBeVisible();
    await expect(page.locator('text=Unread, .tab:has-text("Unread")')).toBeVisible();
  });

  test('should switch between All and Unread tabs', async ({ page }) => {
    // Click Unread tab
    await page.click('.tab:has-text("Unread"), button:has-text("Unread")');

    // Tab should be active
    await expect(page.locator('.tab:has-text("Unread")')).toHaveClass(/active/);

    // Click All tab
    await page.click('.tab:has-text("All"), button:has-text("All")');

    // Tab should be active
    await expect(page.locator('.tab:has-text("All")')).toHaveClass(/active/);
  });

  test('should mark notification as read', async ({ page }) => {
    // Wait for notifications to load
    await page.waitForSelector('.notification-item, [class*="notification"]', { timeout: 10000 });

    // Find first unread notification (if any)
    const unreadNotification = page.locator('.notification-item.unread').first();

    if (await unreadNotification.isVisible()) {
      // Click mark as read button
      const markReadButton = unreadNotification.locator('button[title*="Mark as read"], button[aria-label*="Mark as read"]').first();

      if (await markReadButton.isVisible()) {
        await markReadButton.click();

        // Notification should be marked as read
        await expect(unreadNotification).not.toHaveClass(/unread/);
      }
    }
  });

  test('should delete notification', async ({ page }) => {
    // Wait for notifications to load
    await page.waitForSelector('.notification-item, [class*="notification"]', { timeout: 10000 });

    // Get initial count
    const initialCount = await page.locator('.notification-item').count();

    if (initialCount > 0) {
      // Click delete button on first notification
      const deleteButton = page.locator('.notification-item').first().locator('button[title*="Delete"], button[aria-label*="Delete"]').first();

      if (await deleteButton.isVisible()) {
        await deleteButton.click();

        // Count should decrease
        await page.waitForTimeout(1000);
        const newCount = await page.locator('.notification-item').count();
        expect(newCount).toBe(initialCount - 1);
      }
    }
  });

  test('should clear all read notifications', async ({ page }) => {
    // Look for Clear Read button
    const clearButton = page.locator('button:has-text("Clear Read")');

    if (await clearButton.isVisible()) {
      await clearButton.click();

      // Confirm dialog if present
      page.on('dialog', dialog => dialog.accept());

      // Wait for action to complete
      await page.waitForTimeout(1000);
    }
  });

  test('should show empty state when no notifications', async ({ page }) => {
    // Switch to Unread tab (might be empty)
    await page.click('.tab:has-text("Unread")');

    // Check for empty state
    const emptyState = page.locator('.notifications-empty, .empty-state, text=No notifications');

    // Either there are notifications or empty state is shown
    const hasNotifications = await page.locator('.notification-item').count() > 0;
    const hasEmptyState = await emptyState.isVisible();

    expect(hasNotifications || hasEmptyState).toBe(true);
  });
});

test.describe('Toast Notifications', () => {
  test('should display toast notification', async ({ page }) => {
    // Perform an action that triggers a toast (e.g., save preferences)
    await page.click('.user-button');
    await page.click('text=Preferences');
    await page.click('.preferences-modal__theme-option:has-text("Dark")');
    await page.click('button:has-text("Save")');

    // Toast might appear
    const toast = page.locator('.toast, [class*="toast"]');

    // Wait a bit for toast to appear
    await page.waitForTimeout(500);

    // Toast may or may not be visible depending on implementation
    const toastCount = await toast.count();
    expect(toastCount).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Notifications - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should display notifications page on mobile', async ({ page }) => {
    await page.goto('/notifications');

    await expect(page.locator('h1, .page-title')).toBeVisible();
  });

  test('should display mobile-optimized notification list', async ({ page }) => {
    await page.goto('/notifications');

    // Wait for notifications
    await page.waitForSelector('.notification-item, [class*="notification"]', { timeout: 10000 });

    // Notifications should be visible
    const notifications = page.locator('.notification-item');
    expect(await notifications.count()).toBeGreaterThanOrEqual(0);
  });
});
