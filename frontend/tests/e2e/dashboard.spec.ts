/**
 * Dashboard Flow Tests
 *
 * Tests dashboard statistics, charts, activity feed, and navigation.
 */

import { test, expect } from '@playwright/test';

// Helper to login before each test
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'admin@example.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/');
});

test.describe('Dashboard', () => {
  test('should display dashboard statistics', async ({ page }) => {
    // Wait for dashboard to load
    await expect(page.locator('.brand-title')).toBeVisible();

    // Check for stat cards (should have at least one)
    const statCards = page.locator('.stat-card, [class*="stat"]').first();
    await expect(statCards).toBeVisible({ timeout: 10000 });
  });

  test('should display charts panel', async ({ page }) => {
    // Look for chart container or Recharts components
    const chart = page.locator('[class*="chart"], [class*="recharts"]').first();
    await expect(chart).toBeVisible({ timeout: 10000 });
  });

  test('should display activity feed', async ({ page }) => {
    // Check for activity feed
    const activityFeed = page.locator('[class*="activity"]').first();
    await expect(activityFeed).toBeVisible({ timeout: 10000 });
  });

  test('should navigate between pages', async ({ page }) => {
    // Navigate to Works
    await page.click('text=Browse Works');
    await expect(page).toHaveURL('/works');

    // Navigate to Catalog
    await page.click('text=Catalog Matcher');
    await expect(page).toHaveURL('/catalog');

    // Navigate back to Dashboard
    await page.click('text=Dashboard');
    await expect(page).toHaveURL('/');
  });

  test('should open preferences modal', async ({ page }) => {
    // Open user dropdown
    await page.click('.user-button');
    await expect(page.locator('.user-dropdown')).toBeVisible();

    // Click preferences
    await page.click('text=Preferences');

    // Check modal is open
    await expect(page.locator('.preferences-modal, .modal')).toBeVisible();
  });

  test('should open dashboard layout editor', async ({ page }) => {
    // Open user dropdown
    await page.click('.user-button');
    await expect(page.locator('.user-dropdown')).toBeVisible();

    // Click dashboard layout
    await page.click('text=Dashboard Layout');

    // Check modal is open
    await expect(page.locator('.layout-editor, .modal')).toBeVisible();
  });
});

test.describe('Dashboard - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should open mobile navigation', async ({ page }) => {
    // Click hamburger menu
    const hamburger = page.locator('.mobile-nav-toggle');
    await expect(hamburger).toBeVisible();
    await hamburger.click();

    // Check drawer is open
    await expect(page.locator('.mobile-nav-drawer')).toHaveClass(/open/);
  });

  test('should navigate using mobile menu', async ({ page }) => {
    // Open mobile nav
    await page.click('.mobile-nav-toggle');

    // Click Works link
    await page.click('.mobile-nav-drawer text=Browse Works');

    // Should navigate and close drawer
    await expect(page).toHaveURL('/works');
    await expect(page.locator('.mobile-nav-drawer')).not.toHaveClass(/open/);
  });

  test('should close mobile nav with backdrop click', async ({ page }) => {
    // Open mobile nav
    await page.click('.mobile-nav-toggle');
    await expect(page.locator('.mobile-nav-drawer')).toHaveClass(/open/);

    // Click backdrop
    await page.click('.mobile-nav-backdrop');

    // Should close
    await expect(page.locator('.mobile-nav-drawer')).not.toHaveClass(/open/);
  });
});
