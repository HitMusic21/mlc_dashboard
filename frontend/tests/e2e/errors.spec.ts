/**
 * Error Scenario Tests
 *
 * Tests error handling, 404 pages, API failures, and network issues.
 */

import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'admin@example.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/');
});

test.describe('Error Handling', () => {
  test('should display 404 page for invalid routes', async ({ page }) => {
    await page.goto('/this-page-does-not-exist');

    // Should show 404 page
    await expect(page.locator('text=404, text=Not Found')).toBeVisible();
    await expect(page.locator('text=Go to Dashboard, a[href="/"]')).toBeVisible();
  });

  test('should navigate back to dashboard from 404 page', async ({ page }) => {
    await page.goto('/invalid-route');

    // Click go to dashboard link
    await page.click('text=Go to Dashboard, a[href="/"]');

    // Should navigate to dashboard
    await expect(page).toHaveURL('/');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls and return errors
    await page.route('**/api/v1/works**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });

    // Navigate to works page
    await page.goto('/works');

    // Should display error message (not crash)
    // The page should still render, just showing an error state
    await expect(page.locator('.brand-title')).toBeVisible();
  });

  test('should handle network errors', async ({ page }) => {
    // Simulate network failure
    await page.route('**/api/v1/**', route => {
      route.abort('failed');
    });

    // Try to navigate to a page that needs API data
    await page.goto('/works');

    // Page should still render without crashing
    await expect(page.locator('.brand-title')).toBeVisible();
  });

  test('should display loading states', async ({ page }) => {
    // Delay API response
    await page.route('**/api/v1/works**', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      route.continue();
    });

    // Navigate to works page
    await page.goto('/works');

    // Should show loading indicator
    const loading = page.locator('.loading, .spinner, text=Loading');
    await expect(loading).toBeVisible();
  });
});

test.describe('Form Validation', () => {
  test('should validate email format on login', async ({ page }) => {
    await page.goto('/login');

    // Enter invalid email
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should show validation error or not proceed
    // HTML5 validation will prevent submission
    await expect(page).toHaveURL(/\/login/);
  });

  test('should require all required fields', async ({ page }) => {
    await page.goto('/login');

    // Try to submit without filling fields
    await page.click('button[type="submit"]');

    // Should stay on login page
    await expect(page).toHaveURL(/\/login/);
  });
});

test.describe('Session Management', () => {
  test('should handle expired session', async ({ page }) => {
    // Login
    await expect(page).toHaveURL('/');

    // Clear storage to simulate expired session
    await page.evaluate(() => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    });

    // Try to access protected route
    await page.goto('/works');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);
  });

  test('should handle token refresh', async ({ page }) => {
    // Intercept refresh token endpoint
    let refreshCalled = false;
    await page.route('**/api/v1/auth/refresh', route => {
      refreshCalled = true;
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token'
        })
      });
    });

    // Make an API call that triggers 401
    await page.route('**/api/v1/works', route => {
      if (!refreshCalled) {
        route.fulfill({ status: 401 });
      } else {
        route.continue();
      }
    }, { times: 1 });

    await page.goto('/works');

    // Refresh should be called
    await page.waitForTimeout(2000);
    expect(refreshCalled).toBe(true);
  });
});

test.describe('Accessibility Errors', () => {
  test('should have no console errors on main pages', async ({ page }) => {
    const errors: string[] = [];

    page.on('pageerror', error => {
      errors.push(error.message);
    });

    // Visit main pages
    await page.goto('/');
    await page.goto('/works');
    await page.goto('/catalog');
    await page.goto('/notifications');

    // Should have minimal errors (warnings are ok)
    const criticalErrors = errors.filter(e =>
      e.toLowerCase().includes('error') && !e.toLowerCase().includes('warning')
    );

    expect(criticalErrors.length).toBe(0);
  });
});

test.describe('Error Recovery', () => {
  test('should recover from temporary API failures', async ({ page }) => {
    let callCount = 0;

    // First call fails, second succeeds
    await page.route('**/api/v1/works**', route => {
      callCount++;
      if (callCount === 1) {
        route.fulfill({ status: 500 });
      } else {
        route.continue();
      }
    });

    await page.goto('/works');

    // Try to trigger a refresh/retry
    await page.reload();

    // Second attempt should succeed
    await page.waitForTimeout(1000);
    expect(callCount).toBeGreaterThan(1);
  });
});
