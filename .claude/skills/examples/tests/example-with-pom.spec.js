/**
 * Example test using Page Object Model
 */

const { test, expect } = require('@playwright/test');
const LoginPage = require('../page-objects/LoginPage');
const DashboardPage = require('../page-objects/DashboardPage');

test.describe('Authentication Flow with POM', () => {
  let loginPage;
  let dashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test('should login successfully using page objects', async ({ page }) => {
    // Navigate to login page
    await loginPage.goto();

    // Perform login
    await loginPage.loginAsTestUser();

    // Verify redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);

    // Verify logged in state
    await dashboardPage.verifyLoggedIn('testuser');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await loginPage.goto();

    // Try invalid login
    await loginPage.login('invalid', 'wrong');

    // Verify error message
    await loginPage.verifyErrorMessage('Invalid');
  });

  test('should navigate to forgot password', async ({ page }) => {
    await loginPage.goto();

    await loginPage.clickForgotPassword();

    await expect(page).toHaveURL(/.*forgot-password/);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await loginPage.goto();
    await loginPage.loginAsTestUser();

    // Navigate to dashboard and logout
    await dashboardPage.goto();
    await dashboardPage.logout();

    // Verify redirected to login
    await expect(page).toHaveURL(/.*login/);
  });
});
