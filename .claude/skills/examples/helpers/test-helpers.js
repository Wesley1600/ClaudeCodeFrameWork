/**
 * Test Helper Functions
 * Utility functions for UI testing
 */

const fs = require('fs');
const path = require('path');

/**
 * Take a screenshot with timestamp
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} name - Screenshot name
 */
async function takeScreenshot(page, name) {
  const timestamp = new Date().toISOString().replace(/:/g, '-');
  const filename = `${name}-${timestamp}.png`;
  const screenshotPath = path.join('test-results', 'screenshots', filename);

  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(`Screenshot saved: ${screenshotPath}`);
  return screenshotPath;
}

/**
 * Wait for network to be idle
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {number} timeout - Timeout in milliseconds
 */
async function waitForNetworkIdle(page, timeout = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Fill form with data object
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {Object} formData - Object with field names and values
 */
async function fillForm(page, formData) {
  for (const [field, value] of Object.entries(formData)) {
    const input = page.locator(`[name="${field}"], #${field}`);
    await input.fill(value);
  }
}

/**
 * Select dropdown option by value or text
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} selector - Dropdown selector
 * @param {string} value - Value or text to select
 */
async function selectDropdown(page, selector, value) {
  await page.selectOption(selector, value);
}

/**
 * Check if element exists in DOM
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} selector - Element selector
 * @returns {Promise<boolean>}
 */
async function elementExists(page, selector) {
  const count = await page.locator(selector).count();
  return count > 0;
}

/**
 * Scroll element into view
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} selector - Element selector
 */
async function scrollToElement(page, selector) {
  await page.locator(selector).scrollIntoViewIfNeeded();
}

/**
 * Get all text content from elements
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} selector - Element selector
 * @returns {Promise<string[]>}
 */
async function getAllTextContent(page, selector) {
  const elements = await page.locator(selector).all();
  const texts = [];

  for (const element of elements) {
    texts.push(await element.textContent());
  }

  return texts;
}

/**
 * Wait for API response
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} urlPattern - URL pattern to match
 * @returns {Promise<Object>} Response data
 */
async function waitForApiResponse(page, urlPattern) {
  const response = await page.waitForResponse(
    response => response.url().includes(urlPattern) && response.status() === 200
  );

  return await response.json();
}

/**
 * Mock API endpoint
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} urlPattern - URL pattern to mock
 * @param {Object} mockData - Mock response data
 * @param {number} statusCode - HTTP status code
 */
async function mockApiEndpoint(page, urlPattern, mockData, statusCode = 200) {
  await page.route(urlPattern, route => {
    route.fulfill({
      status: statusCode,
      contentType: 'application/json',
      body: JSON.stringify(mockData)
    });
  });
}

/**
 * Clear browser storage (localStorage, sessionStorage, cookies)
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function clearBrowserStorage(page) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.context().clearCookies();
}

/**
 * Set local storage item
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} key - Storage key
 * @param {any} value - Storage value
 */
async function setLocalStorage(page, key, value) {
  await page.evaluate(
    ({ key, value }) => {
      localStorage.setItem(key, JSON.stringify(value));
    },
    { key, value }
  );
}

/**
 * Get local storage item
 * @param {import('@playwright/test').Page} page - Playwright page
 * @param {string} key - Storage key
 * @returns {Promise<any>}
 */
async function getLocalStorage(page, key) {
  return await page.evaluate(
    key => {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    },
    key
  );
}

/**
 * Generate test report
 * @param {Object} results - Test results object
 */
function generateTestReport(results) {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: results.total,
      passed: results.passed,
      failed: results.failed,
      skipped: results.skipped,
      duration: results.duration
    },
    tests: results.tests
  };

  const reportPath = path.join('test-results', 'report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log('\n=== Test Report ===');
  console.log(`Total: ${report.summary.total}`);
  console.log(`✅ Passed: ${report.summary.passed}`);
  console.log(`❌ Failed: ${report.summary.failed}`);
  console.log(`⏭️  Skipped: ${report.summary.skipped}`);
  console.log(`⏱️  Duration: ${report.summary.duration}ms`);
  console.log(`\nReport saved: ${reportPath}\n`);

  return report;
}

/**
 * Retry function with exponential backoff
 * @param {Function} fn - Function to retry
 * @param {number} maxRetries - Maximum number of retries
 * @param {number} delay - Initial delay in milliseconds
 */
async function retryWithBackoff(fn, maxRetries = 3, delay = 1000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
}

/**
 * Simulate slow network
 * @param {import('@playwright/test').Page} page - Playwright page
 */
async function simulateSlowNetwork(page) {
  const client = await page.context().newCDPSession(page);
  await client.send('Network.emulateNetworkConditions', {
    offline: false,
    downloadThroughput: (500 * 1024) / 8, // 500 kb/s
    uploadThroughput: (500 * 1024) / 8,
    latency: 400 // ms
  });
}

/**
 * Get console logs from page
 * @param {import('@playwright/test').Page} page - Playwright page
 * @returns {Array} Array of console messages
 */
function captureConsoleLogs(page) {
  const logs = [];

  page.on('console', msg => {
    logs.push({
      type: msg.type(),
      text: msg.text(),
      location: msg.location()
    });
  });

  return logs;
}

/**
 * Detect and log JavaScript errors
 * @param {import('@playwright/test').Page} page - Playwright page
 * @returns {Array} Array of errors
 */
function capturePageErrors(page) {
  const errors = [];

  page.on('pageerror', error => {
    errors.push({
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  });

  return errors;
}

module.exports = {
  takeScreenshot,
  waitForNetworkIdle,
  fillForm,
  selectDropdown,
  elementExists,
  scrollToElement,
  getAllTextContent,
  waitForApiResponse,
  mockApiEndpoint,
  clearBrowserStorage,
  setLocalStorage,
  getLocalStorage,
  generateTestReport,
  retryWithBackoff,
  simulateSlowNetwork,
  captureConsoleLogs,
  capturePageErrors
};
