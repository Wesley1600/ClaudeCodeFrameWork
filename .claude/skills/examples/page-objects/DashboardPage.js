/**
 * Page Object Model - Dashboard Page
 */

class DashboardPage {
  constructor(page) {
    this.page = page;

    // Locators
    this.welcomeMessage = page.locator('.welcome-message');
    this.userProfile = page.locator('[data-testid="user-profile"]');
    this.logoutButton = page.locator('[data-testid="logout-button"]');
    this.sidebar = page.locator('.sidebar');
    this.mainContent = page.locator('.main-content');
    this.notifications = page.locator('.notification-badge');
  }

  /**
   * Navigate to dashboard
   */
  async goto(baseUrl = 'https://example.com') {
    await this.page.goto(`${baseUrl}/dashboard`);
  }

  /**
   * Verify user is logged in
   * @param {string} expectedUsername - Expected username to display
   */
  async verifyLoggedIn(expectedUsername) {
    await this.welcomeMessage.waitFor({ state: 'visible' });
    const welcomeText = await this.welcomeMessage.textContent();

    if (!welcomeText.includes(expectedUsername)) {
      throw new Error(`Expected welcome message to contain "${expectedUsername}"`);
    }
  }

  /**
   * Logout from the application
   */
  async logout() {
    await this.logoutButton.click();
  }

  /**
   * Navigate to a specific section via sidebar
   * @param {string} sectionName - Name of the section to navigate to
   */
  async navigateToSection(sectionName) {
    await this.sidebar.locator(`a:has-text("${sectionName}")`).click();
  }

  /**
   * Get notification count
   * @returns {Promise<number>}
   */
  async getNotificationCount() {
    const count = await this.notifications.textContent();
    return parseInt(count, 10);
  }

  /**
   * Check if specific widget is visible
   * @param {string} widgetName - Name of the widget
   * @returns {Promise<boolean>}
   */
  async isWidgetVisible(widgetName) {
    const widget = this.page.locator(`[data-widget="${widgetName}"]`);
    return await widget.isVisible();
  }
}

module.exports = DashboardPage;
