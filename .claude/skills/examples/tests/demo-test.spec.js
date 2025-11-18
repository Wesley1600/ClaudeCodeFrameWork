/**
 * Demo Test - Real World Example
 * This test runs against a real website to demonstrate the automated-ui-testing skill
 *
 * This example uses example.com which is a public demo site
 */

const { test, expect } = require('@playwright/test');

test.describe('Demo: Real Website Testing', () => {
  test('should load example.com homepage', async ({ page }) => {
    console.log('🌐 Navigating to example.com...');
    await page.goto('https://example.com');

    // Verify page title
    await expect(page).toHaveTitle(/Example Domain/);
    console.log('✅ Page title verified');

    // Verify heading is visible
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toHaveText('Example Domain');
    console.log('✅ Heading verified');

    // Take screenshot
    await page.screenshot({ path: 'test-results/example-homepage.png' });
    console.log('📸 Screenshot saved');

    // Verify "More information" link
    const link = page.locator('a:has-text("More information")');
    await expect(link).toBeVisible();
    console.log('✅ Link found');

    // Get page text content
    const bodyText = await page.locator('body').textContent();
    expect(bodyText).toContain('illustrative examples');
    console.log('✅ Content verified');
  });

  test('should navigate to IANA website via link', async ({ page }) => {
    await page.goto('https://example.com');

    console.log('🔗 Clicking "More information" link...');

    // Click the link and wait for navigation
    await page.click('a:has-text("More information")');

    // Wait for navigation
    await page.waitForLoadState('networkidle');

    // Verify we're on IANA website
    expect(page.url()).toContain('iana.org');
    console.log('✅ Navigation successful');

    await page.screenshot({ path: 'test-results/iana-page.png' });
    console.log('📸 Screenshot saved');
  });

  test('should verify page structure and elements', async ({ page }) => {
    await page.goto('https://example.com');

    console.log('🔍 Inspecting page structure...');

    // Check for paragraph elements
    const paragraphs = page.locator('p');
    const count = await paragraphs.count();
    expect(count).toBeGreaterThan(0);
    console.log(`✅ Found ${count} paragraph(s)`);

    // Verify div container exists
    const div = page.locator('div');
    await expect(div.first()).toBeVisible();
    console.log('✅ Container div verified');

    // Check viewport size
    const viewportSize = page.viewportSize();
    console.log(`📐 Viewport: ${viewportSize.width}x${viewportSize.height}`);

    // Get computed styles
    const bgColor = await page.locator('body').evaluate(el => {
      return window.getComputedStyle(el).backgroundColor;
    });
    console.log(`🎨 Background color: ${bgColor}`);
  });

  test('should test responsive behavior', async ({ page }) => {
    console.log('📱 Testing responsive design...');

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('https://example.com');
    await page.screenshot({ path: 'test-results/example-mobile.png' });
    console.log('✅ Mobile view captured (375x667)');

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    await page.screenshot({ path: 'test-results/example-tablet.png' });
    console.log('✅ Tablet view captured (768x1024)');

    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.reload();
    await page.screenshot({ path: 'test-results/example-desktop.png' });
    console.log('✅ Desktop view captured (1920x1080)');

    // Verify heading is visible in all viewports
    await expect(page.locator('h1')).toBeVisible();
    console.log('✅ Content visible across all viewports');
  });

  test('should measure page performance', async ({ page }) => {
    console.log('⏱️ Measuring page performance...');

    const startTime = Date.now();

    await page.goto('https://example.com');

    const loadTime = Date.now() - startTime;
    console.log(`⚡ Page loaded in ${loadTime}ms`);

    // Get performance metrics
    const metrics = await page.evaluate(() => {
      const perfData = window.performance.timing;
      return {
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
        loadComplete: perfData.loadEventEnd - perfData.navigationStart,
        domInteractive: perfData.domInteractive - perfData.navigationStart
      };
    });

    console.log('📊 Performance metrics:');
    console.log(`   - DOM Interactive: ${metrics.domInteractive}ms`);
    console.log(`   - DOM Content Loaded: ${metrics.domContentLoaded}ms`);
    console.log(`   - Load Complete: ${metrics.loadComplete}ms`);

    // Verify page loads reasonably fast
    expect(metrics.loadComplete).toBeLessThan(5000);
    console.log('✅ Performance check passed');
  });

  test('should verify accessibility basics', async ({ page }) => {
    await page.goto('https://example.com');

    console.log('♿ Checking accessibility...');

    // Check for heading hierarchy
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThan(0);
    console.log(`✅ Found ${h1Count} h1 heading(s)`);

    // Check links have text
    const links = await page.locator('a').all();
    for (const link of links) {
      const text = await link.textContent();
      expect(text.trim()).not.toBe('');
    }
    console.log(`✅ All ${links.length} links have text content`);

    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement.tagName);
    console.log(`⌨️ First tab focus: ${focusedElement}`);

    console.log('✅ Basic accessibility checks passed');
  });
});

test.describe('Demo: Error Handling', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    console.log('🔌 Testing offline scenario...');

    // Set offline mode
    await page.context().setOffline(true);

    try {
      await page.goto('https://example.com', { timeout: 5000 });
    } catch (error) {
      console.log('✅ Caught expected network error:', error.message);
      expect(error.message).toContain('net::ERR');
    }

    // Restore connection
    await page.context().setOffline(false);
    console.log('✅ Error handling test passed');
  });

  test('should handle slow network conditions', async ({ page }) => {
    console.log('🐢 Testing slow network...');

    // Simulate slow 3G
    const client = await page.context().newCDPSession(page);
    await client.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: (500 * 1024) / 8, // 500kb/s
      uploadThroughput: (500 * 1024) / 8,
      latency: 400 // 400ms
    });

    const startTime = Date.now();
    await page.goto('https://example.com');
    const loadTime = Date.now() - startTime;

    console.log(`🐌 Page loaded in ${loadTime}ms with slow network`);
    expect(loadTime).toBeGreaterThan(400); // Should be affected by latency

    console.log('✅ Slow network test passed');
  });
});

// Hooks for better logging
test.beforeEach(async ({ page }, testInfo) => {
  console.log(`\n🧪 Starting test: ${testInfo.title}`);
});

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === 'failed') {
    console.log(`❌ Test failed: ${testInfo.title}`);

    // Take failure screenshot
    const screenshotPath = `test-results/failure-${Date.now()}.png`;
    await page.screenshot({ path: screenshotPath });
    console.log(`📸 Failure screenshot: ${screenshotPath}`);
  } else {
    console.log(`✅ Test passed: ${testInfo.title}\n`);
  }
});
