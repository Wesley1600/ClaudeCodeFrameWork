/**
 * Example UI Test Suite using Playwright
 * This demonstrates the automated-ui-testing skill capabilities
 */

const { test, expect } = require('@playwright/test');

// ============================================================================
// EXAMPLE 1: Basic Form Testing
// ============================================================================

test.describe('Contact Form Tests', () => {
  test('should submit contact form successfully', async ({ page }) => {
    // Navigate to the page
    await page.goto('https://example.com/contact');

    // Fill out the form
    await page.fill('#name', 'John Doe');
    await page.fill('#email', 'john@example.com');
    await page.fill('#subject', 'Test Inquiry');
    await page.fill('#message', 'This is a test message');

    // Submit the form
    await page.click('button[type="submit"]');

    // Verify success message
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Thank you');
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('https://example.com/contact');

    // Try to submit without filling
    await page.click('button[type="submit"]');

    // Verify error messages appear
    await expect(page.locator('#name-error')).toBeVisible();
    await expect(page.locator('#email-error')).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('https://example.com/contact');

    // Enter invalid email
    await page.fill('#email', 'invalid-email');
    await page.click('button[type="submit"]');

    // Verify email validation error
    await expect(page.locator('#email-error')).toContainText('valid email');
  });
});

// ============================================================================
// EXAMPLE 2: Authentication Testing
// ============================================================================

test.describe('User Authentication', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('https://example.com/login');

    // Enter credentials
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');

    // Click login button
    await page.click('button:has-text("Log in")');

    // Verify redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('.user-profile')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('https://example.com/login');

    await page.fill('[name="username"]', 'wronguser');
    await page.fill('[name="password"]', 'wrongpass');
    await page.click('button:has-text("Log in")');

    // Verify error message
    await expect(page.locator('.error-message')).toContainText('Invalid');
  });

  test('should logout successfully', async ({ page }) => {
    // Assume we're logged in
    await page.goto('https://example.com/dashboard');

    // Click logout
    await page.click('[data-testid="logout-button"]');

    // Verify redirect to login
    await expect(page).toHaveURL(/.*login/);
  });
});

// ============================================================================
// EXAMPLE 3: E-Commerce Shopping Flow
// ============================================================================

test.describe('Shopping Cart', () => {
  test('should add item to cart', async ({ page }) => {
    await page.goto('https://example.com/products');

    // Click on a product
    await page.click('.product-card:first-child');

    // Add to cart
    await page.click('button:has-text("Add to Cart")');

    // Verify cart count updated
    await expect(page.locator('.cart-count')).toHaveText('1');

    // Navigate to cart
    await page.click('.cart-icon');

    // Verify item in cart
    await expect(page.locator('.cart-item')).toHaveCount(1);
  });

  test('should update item quantity', async ({ page }) => {
    await page.goto('https://example.com/cart');

    // Get initial price
    const initialPrice = await page.locator('.total-price').textContent();

    // Increase quantity
    await page.click('[data-testid="increase-quantity"]');

    // Verify quantity and price updated
    await expect(page.locator('.item-quantity')).toHaveText('2');
    const newPrice = await page.locator('.total-price').textContent();
    expect(newPrice).not.toBe(initialPrice);
  });

  test('should remove item from cart', async ({ page }) => {
    await page.goto('https://example.com/cart');

    // Remove item
    await page.click('[data-testid="remove-item"]');

    // Verify cart is empty
    await expect(page.locator('.empty-cart-message')).toBeVisible();
  });
});

// ============================================================================
// EXAMPLE 4: Navigation Testing
// ============================================================================

test.describe('Website Navigation', () => {
  test('should navigate through main menu', async ({ page }) => {
    await page.goto('https://example.com');

    // Click About link
    await page.click('nav a:has-text("About")');
    await expect(page).toHaveURL(/.*about/);

    // Click Services link
    await page.click('nav a:has-text("Services")');
    await expect(page).toHaveURL(/.*services/);

    // Click Contact link
    await page.click('nav a:has-text("Contact")');
    await expect(page).toHaveURL(/.*contact/);
  });

  test('should handle breadcrumb navigation', async ({ page }) => {
    await page.goto('https://example.com/products/category/item');

    // Click breadcrumb
    await page.click('.breadcrumb a:has-text("Category")');

    // Verify navigation
    await expect(page).toHaveURL(/.*category/);
  });
});

// ============================================================================
// EXAMPLE 5: Search Functionality
// ============================================================================

test.describe('Search', () => {
  test('should search and display results', async ({ page }) => {
    await page.goto('https://example.com');

    // Enter search query
    await page.fill('[data-testid="search-input"]', 'laptop');

    // Submit search
    await page.press('[data-testid="search-input"]', 'Enter');

    // Verify results displayed
    await expect(page.locator('.search-results')).toBeVisible();
    await expect(page.locator('.result-item')).toHaveCount.greaterThan(0);
  });

  test('should show no results message', async ({ page }) => {
    await page.goto('https://example.com');

    await page.fill('[data-testid="search-input"]', 'xyzabc123notfound');
    await page.press('[data-testid="search-input"]', 'Enter');

    await expect(page.locator('.no-results-message')).toBeVisible();
  });
});

// ============================================================================
// EXAMPLE 6: Responsive Design Testing
// ============================================================================

test.describe('Responsive Design', () => {
  test('should display mobile menu on small screens', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('https://example.com');

    // Verify hamburger menu visible
    await expect(page.locator('.hamburger-menu')).toBeVisible();

    // Verify desktop menu hidden
    await expect(page.locator('.desktop-menu')).not.toBeVisible();

    // Click hamburger
    await page.click('.hamburger-menu');

    // Verify mobile menu opens
    await expect(page.locator('.mobile-nav')).toBeVisible();
  });

  test('should display desktop layout on large screens', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('https://example.com');

    await expect(page.locator('.desktop-menu')).toBeVisible();
    await expect(page.locator('.hamburger-menu')).not.toBeVisible();
  });
});

// ============================================================================
// EXAMPLE 7: API Interception and Mocking
// ============================================================================

test.describe('API Testing', () => {
  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API to return error
    await page.route('**/api/products', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    await page.goto('https://example.com/products');

    // Verify error message displayed
    await expect(page.locator('.error-banner')).toBeVisible();
    await expect(page.locator('.error-banner')).toContainText('error');
  });

  test('should verify request payload', async ({ page }) => {
    let requestBody;

    // Intercept API request
    await page.route('**/api/contact', route => {
      requestBody = route.request().postDataJSON();
      route.fulfill({
        status: 200,
        body: JSON.stringify({ success: true })
      });
    });

    await page.goto('https://example.com/contact');

    await page.fill('#name', 'Test User');
    await page.fill('#email', 'test@example.com');
    await page.click('button[type="submit"]');

    // Verify request payload
    expect(requestBody.name).toBe('Test User');
    expect(requestBody.email).toBe('test@example.com');
  });
});

// ============================================================================
// EXAMPLE 8: File Upload Testing
// ============================================================================

test.describe('File Upload', () => {
  test('should upload file successfully', async ({ page }) => {
    await page.goto('https://example.com/upload');

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-files/sample.pdf');

    // Submit
    await page.click('button:has-text("Upload")');

    // Verify success
    await expect(page.locator('.upload-success')).toBeVisible();
  });
});

// ============================================================================
// EXAMPLE 9: Accessibility Testing
// ============================================================================

test.describe('Accessibility', () => {
  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('https://example.com');

    // Tab through elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Verify focus visible
    const focusedElement = await page.evaluate(() => document.activeElement.tagName);
    expect(['A', 'BUTTON', 'INPUT']).toContain(focusedElement);

    // Press Enter to activate
    await page.keyboard.press('Enter');
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('https://example.com');

    // Check ARIA labels exist
    const searchInput = page.locator('[data-testid="search-input"]');
    await expect(searchInput).toHaveAttribute('aria-label');
  });
});

// ============================================================================
// EXAMPLE 10: Visual Regression Testing
// ============================================================================

test.describe('Visual Regression', () => {
  test('should match homepage screenshot', async ({ page }) => {
    await page.goto('https://example.com');

    // Take screenshot and compare
    await expect(page).toHaveScreenshot('homepage.png', {
      fullPage: true,
      maxDiffPixels: 100
    });
  });

  test('should match specific component', async ({ page }) => {
    await page.goto('https://example.com');

    const header = page.locator('header');
    await expect(header).toHaveScreenshot('header.png');
  });
});
