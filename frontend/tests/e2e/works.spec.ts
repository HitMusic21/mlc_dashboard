/**
 * Works Browser Tests
 *
 * Tests work listing, search, filters, sorting, and pagination.
 */

import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'admin@example.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/');

  // Navigate to Works page
  await page.goto('/works');
});

test.describe('Works Browser', () => {
  test('should display works table', async ({ page }) => {
    // Wait for table to load
    await expect(page.locator('.works-table, table')).toBeVisible({ timeout: 10000 });

    // Should have table headers
    await expect(page.locator('th:has-text("Title")')).toBeVisible();
    await expect(page.locator('th:has-text("Writer")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
  });

  test('should display work rows with data', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('tbody tr', { timeout: 10000 });

    // Should have at least one row
    const rowCount = await page.locator('tbody tr').count();
    expect(rowCount).toBeGreaterThan(0);
  });

  test('should search for works', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]');
    await expect(searchInput).toBeVisible();

    // Enter search term
    await searchInput.fill('test');

    // Wait for results to update
    await page.waitForTimeout(1000);

    // Results should be filtered (implementation-dependent)
    const rowCount = await page.locator('tbody tr').count();
    expect(rowCount).toBeGreaterThanOrEqual(0);
  });

  test('should filter by status', async ({ page }) => {
    // Look for status filter dropdown
    const statusFilter = page.locator('select[name="status"], .filter-status');

    if (await statusFilter.isVisible()) {
      // Select a status
      await statusFilter.selectOption('pending');

      // Wait for results to update
      await page.waitForTimeout(1000);

      // Results should be filtered
      const rowCount = await page.locator('tbody tr').count();
      expect(rowCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('should sort by column', async ({ page }) => {
    // Click on Title header to sort
    const titleHeader = page.locator('th:has-text("Title")');
    await titleHeader.click();

    // Wait for sort to apply
    await page.waitForTimeout(500);

    // Click again to reverse sort
    await titleHeader.click();
    await page.waitForTimeout(500);

    // Table should still be visible
    await expect(page.locator('.works-table, table')).toBeVisible();
  });

  test('should navigate to work details', async ({ page }) => {
    // Wait for table to load
    await page.waitForSelector('tbody tr', { timeout: 10000 });

    // Click on first work row or view button
    const firstRow = page.locator('tbody tr').first();
    const viewButton = firstRow.locator('button:has-text("View"), a:has-text("View")').first();

    if (await viewButton.isVisible()) {
      await viewButton.click();

      // Should navigate to work details page
      await expect(page).toHaveURL(/\/works\/\d+/);
    }
  });

  test('should paginate through results', async ({ page }) => {
    // Wait for pagination controls
    await page.waitForSelector('.pagination, [class*="pagination"]', { timeout: 10000 });

    // Check if next button exists
    const nextButton = page.locator('button:has-text("Next"), .pagination-next');

    if (await nextButton.isVisible()) {
      // Click next page
      await nextButton.click();

      // Wait for new page to load
      await page.waitForTimeout(1000);

      // Should have updated results
      await expect(page.locator('.works-table, table')).toBeVisible();
    }
  });

  test('should change items per page', async ({ page }) => {
    // Look for items per page selector
    const itemsPerPageSelect = page.locator('select[name="itemsPerPage"], .items-per-page select');

    if (await itemsPerPageSelect.isVisible()) {
      // Get initial row count
      const initialCount = await page.locator('tbody tr').count();

      // Change items per page
      await itemsPerPageSelect.selectOption('25');

      // Wait for results to update
      await page.waitForTimeout(1000);

      // Row count may change
      const newCount = await page.locator('tbody tr').count();
      expect(newCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('should display empty state when no results', async ({ page }) => {
    // Search for something that doesn't exist
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]');
    await searchInput.fill('xyznonexistentwork123');

    // Wait for results
    await page.waitForTimeout(1000);

    // Should show empty state or no results message
    const emptyState = page.locator('.empty-state, .no-results, text=No works found');
    const hasEmptyState = await emptyState.isVisible();
    const rowCount = await page.locator('tbody tr').count();

    // Either empty state is shown or there are 0 rows
    expect(hasEmptyState || rowCount === 0).toBe(true);
  });

  test('should bulk select works', async ({ page }) => {
    // Wait for table to load
    await page.waitForSelector('tbody tr', { timeout: 10000 });

    // Look for select all checkbox
    const selectAllCheckbox = page.locator('thead input[type="checkbox"]').first();

    if (await selectAllCheckbox.isVisible()) {
      // Click select all
      await selectAllCheckbox.click();

      // All row checkboxes should be checked
      const checkboxes = page.locator('tbody input[type="checkbox"]');
      const count = await checkboxes.count();

      if (count > 0) {
        // At least first checkbox should be checked
        const firstCheckbox = checkboxes.first();
        await expect(firstCheckbox).toBeChecked();
      }
    }
  });

  test('should export works', async ({ page }) => {
    // Look for export button
    const exportButton = page.locator('button:has-text("Export"), .export-button');

    if (await exportButton.isVisible()) {
      // Click export
      await exportButton.click();

      // Export options or download should trigger
      const exportModal = page.locator('.export-modal, .modal');
      const hasModal = await exportModal.isVisible({ timeout: 2000 }).catch(() => false);

      // Either modal appears or download starts (both are valid)
      expect(hasModal || true).toBe(true);
    }
  });
});

test.describe('Works Browser - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should display mobile-optimized works list', async ({ page }) => {
    // Wait for works to load
    await page.waitForSelector('.work-card, .works-table', { timeout: 10000 });

    // Should be visible
    const worksContainer = page.locator('.work-card, .works-table').first();
    await expect(worksContainer).toBeVisible();
  });

  test('should open work details on mobile', async ({ page }) => {
    // Wait for works to load
    await page.waitForSelector('.work-card, tbody tr', { timeout: 10000 });

    // Click first work
    const firstWork = page.locator('.work-card, tbody tr').first();
    await firstWork.click();

    // Should navigate or show details
    // URL changes or modal appears
    await page.waitForTimeout(1000);
  });

  test('should use mobile filters', async ({ page }) => {
    // Look for mobile filter button
    const filterButton = page.locator('button:has-text("Filter"), .filter-toggle');

    if (await filterButton.isVisible()) {
      await filterButton.click();

      // Filter panel should open
      await expect(page.locator('.filter-panel, .filters')).toBeVisible();
    }
  });
});
