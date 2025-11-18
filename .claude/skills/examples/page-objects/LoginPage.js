/**
 * Page Object Model (POM) Example - Login Page
 * Demonstrates reusable page objects for UI testing
 */

class LoginPage {
  /**
   * Initialize the Login Page
   * @param {import('@playwright/test').Page} page - Playwright page object
   */
  constructor(page) {
    this.page = page;

    // Define locators
    this.usernameInput = page.locator('[data-testid="username"]');
    this.passwordInput = page.locator('[data-testid="password"]');
    this.loginButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
    this.rememberMeCheckbox = page.locator('#remember-me');
    this.forgotPasswordLink = page.locator('a:has-text("Forgot Password")');
    this.signUpLink = page.locator('a:has-text("Sign Up")');
  }

  /**
   * Navigate to the login page
   * @param {string} baseUrl - The base URL of the application
   */
  async goto(baseUrl = 'https://example.com') {
    await this.page.goto(`${baseUrl}/login`);
  }

  /**
   * Perform login action
   * @param {string} username - Username
   * @param {string} password - Password
   * @param {boolean} rememberMe - Whether to check "Remember Me"
   */
  async login(username, password, rememberMe = false) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);

    if (rememberMe) {
      await this.rememberMeCheckbox.check();
    }

    await this.loginButton.click();
  }

  /**
   * Quick login for valid user
   * @param {string} username - Username (defaults to test user)
   * @param {string} password - Password (defaults to test password)
   */
  async loginAsTestUser(username = 'testuser', password = 'Test@1234') {
    await this.login(username, password);
  }

  /**
   * Verify error message is displayed
   * @param {string} expectedMessage - Expected error message (partial match)
   */
  async verifyErrorMessage(expectedMessage) {
    await this.errorMessage.waitFor({ state: 'visible' });
    const actualMessage = await this.errorMessage.textContent();
    if (!actualMessage.includes(expectedMessage)) {
      throw new Error(`Expected error message to contain "${expectedMessage}", but got "${actualMessage}"`);
    }
  }

  /**
   * Click forgot password link
   */
  async clickForgotPassword() {
    await this.forgotPasswordLink.click();
  }

  /**
   * Click sign up link
   */
  async clickSignUp() {
    await this.signUpLink.click();
  }

  /**
   * Check if login button is enabled
   * @returns {Promise<boolean>}
   */
  async isLoginButtonEnabled() {
    return await this.loginButton.isEnabled();
  }

  /**
   * Get validation state of username field
   * @returns {Promise<string>}
   */
  async getUsernameValidationState() {
    return await this.usernameInput.getAttribute('aria-invalid');
  }

  /**
   * Clear the login form
   */
  async clearForm() {
    await this.usernameInput.clear();
    await this.passwordInput.clear();
  }
}

module.exports = LoginPage;
