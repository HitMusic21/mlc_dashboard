/**
 * Authentication Flow Tests
 *
 * Tests login, logout, session management, and authentication errors.
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/BWARM Dashboard/);
    await expect(page.locator('h2')).toContainText(/sign in/i);
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.click('button[type="submit"]');

    // Form should not submit and stay on login page
    await expect(page).toHaveURL(/\/login/);
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Wait for error message
    await expect(page.locator('.login-error, .alert-error')).toBeVisible();
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Use test credentials
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/');
    await expect(page.locator('.brand-title')).toContainText('BWARM Dashboard');
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/login/);
  });

  test('should maintain session after page reload', async ({ page }) => {
    // Login first
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');

    // Reload page
    await page.reload();

    // Should still be on dashboard
    await expect(page).toHaveURL('/');
    await expect(page.locator('.brand-title')).toBeVisible();
  });

  test('should successfully logout', async ({ page }) => {
    // Login first
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');

    // Open user dropdown
    await page.click('.user-button');
    await expect(page.locator('.user-dropdown')).toBeVisible();

    // Click logout
    await page.click('text=Logout');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);
  });

  test('should prevent access to protected routes after logout', async ({ page }) => {
    // Login
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');

    // Logout
    await page.click('.user-button');
    await page.click('text=Logout');
    await expect(page).toHaveURL(/\/login/);

    // Try to access protected route
    await page.goto('/works');
    await expect(page).toHaveURL(/\/login/);
  });
});

test.describe('Authentication - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should login on mobile device', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/');
  });
});
