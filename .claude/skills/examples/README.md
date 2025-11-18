# Automated UI Testing Examples

This directory contains comprehensive examples for the **automated-ui-testing** skill in Claude Code.

## 📁 Directory Structure

```
examples/
├── README.md                          # This file
├── package.json                       # Dependencies
├── playwright.config.js               # Test configuration
├── ui-testing-example.js              # Comprehensive test examples
├── page-objects/                      # Page Object Model examples
│   ├── LoginPage.js                   # Login page object
│   └── DashboardPage.js               # Dashboard page object
├── helpers/                           # Test utilities
│   └── test-helpers.js                # Helper functions
└── tests/                             # Test suites
    ├── global-setup.js                # Global test setup
    ├── global-teardown.js             # Global test cleanup
    └── example-with-pom.spec.js       # POM-based tests
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

This will install:
- `@playwright/test` - Modern testing framework
- Chromium, Firefox, and WebKit browsers

### 2. Run Tests

```bash
# Run all tests
npm test

# Run specific test file
npx playwright test tests/example-with-pom.spec.js

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific browser
npx playwright test --project=chromium

# Run in debug mode
npx playwright test --debug
```

### 3. View Test Results

```bash
# Open HTML report
npx playwright show-report test-results/html-report

# View JSON results
cat test-results/results.json
```

## 📚 Examples Included

### 1. Basic Form Testing
- Fill and submit forms
- Validate input fields
- Test error messages
- Verify success states

### 2. Authentication Testing
- Login flows
- Logout functionality
- Session management
- Error handling

### 3. E-Commerce Testing
- Product browsing
- Shopping cart operations
- Checkout process
- Order confirmation

### 4. Navigation Testing
- Menu navigation
- Breadcrumbs
- URL validation
- Deep linking

### 5. Search Functionality
- Search input and submission
- Results validation
- Empty results handling
- Search filters

### 6. Responsive Design
- Mobile viewports
- Tablet layouts
- Desktop views
- Breakpoint testing

### 7. API Testing
- Request interception
- Response mocking
- Payload validation
- Error simulation

### 8. File Upload
- Single file upload
- Multiple files
- File type validation
- Upload progress

### 9. Accessibility Testing
- Keyboard navigation
- ARIA labels
- Focus management
- Screen reader compatibility

### 10. Visual Regression
- Screenshot comparison
- Component snapshots
- Layout verification
- Pixel-perfect testing

## 🎯 Page Object Model (POM)

The `page-objects/` directory demonstrates the Page Object Model pattern:

### LoginPage.js
```javascript
const LoginPage = require('./page-objects/LoginPage');

const loginPage = new LoginPage(page);
await loginPage.goto();
await loginPage.loginAsTestUser();
```

### DashboardPage.js
```javascript
const DashboardPage = require('./page-objects/DashboardPage');

const dashboardPage = new DashboardPage(page);
await dashboardPage.verifyLoggedIn('username');
await dashboardPage.navigateToSection('Settings');
```

## 🛠️ Helper Functions

The `helpers/test-helpers.js` file provides useful utilities:

```javascript
const {
  takeScreenshot,
  fillForm,
  waitForApiResponse,
  mockApiEndpoint,
  clearBrowserStorage,
  generateTestReport
} = require('./helpers/test-helpers');

// Take screenshot
await takeScreenshot(page, 'error-state');

// Fill form easily
await fillForm(page, {
  name: 'John Doe',
  email: 'john@example.com',
  message: 'Hello!'
});

// Wait for API
const data = await waitForApiResponse(page, '/api/users');

// Mock API endpoint
await mockApiEndpoint(page, '**/api/products', { products: [] });
```

## 🎨 Customization

### Change Base URL

Edit `playwright.config.js`:
```javascript
use: {
  baseURL: 'https://your-app.com',
}
```

Or use environment variable:
```bash
BASE_URL=https://staging.example.com npm test
```

### Add Custom Browsers

```javascript
projects: [
  {
    name: 'custom-chromium',
    use: {
      ...devices['Desktop Chrome'],
      viewport: { width: 1920, height: 1080 },
    },
  },
]
```

### Configure Retries

```javascript
retries: process.env.CI ? 3 : 1,
```

### Adjust Timeouts

```javascript
timeout: 60 * 1000, // 60 seconds
```

## 🐛 Debugging

### Debug Mode
```bash
npx playwright test --debug
```

### Headed Mode
```bash
npx playwright test --headed --slow-mo=1000
```

### Trace Viewer
```bash
npx playwright show-trace test-results/artifacts/trace.zip
```

### Console Logs
```javascript
page.on('console', msg => console.log(msg.text()));
```

## 📊 Reporters

### Built-in Reporters
- `list` - Simple list output
- `html` - Interactive HTML report
- `json` - JSON results file
- `junit` - JUnit XML format
- `github` - GitHub Actions annotations

### Custom Reporter
```javascript
reporter: [
  ['./custom-reporter.js', { outputFile: 'results.txt' }]
]
```

## 🔧 CI/CD Integration

### GitHub Actions

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

### GitLab CI

```yaml
test:
  image: mcr.microsoft.com/playwright:latest
  script:
    - npm ci
    - npm test
  artifacts:
    when: always
    paths:
      - test-results/
```

## 🌐 Environment Variables

```bash
# Base URL
BASE_URL=https://example.com

# Enable slow motion
SLOW_MO=1000

# Start dev server before tests
START_SERVER=true

# CI mode
CI=true
```

## 📖 Learning Resources

- [Playwright Documentation](https://playwright.dev)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)
- [Page Object Model Guide](https://playwright.dev/docs/pom)
- [API Testing](https://playwright.dev/docs/api-testing)

## 🆘 Common Issues

### Browser Install Fails
```bash
npx playwright install --force
```

### Permission Errors
```bash
sudo npx playwright install-deps
```

### Port Already in Use
```bash
# Kill process on port 3000
npx kill-port 3000
```

### Test Timeouts
Increase timeout in config:
```javascript
timeout: 60 * 1000
```

## 💡 Tips

1. **Use data-testid**: Add `data-testid` attributes to make selectors more stable
2. **Avoid fixed waits**: Use auto-waiting instead of `page.waitForTimeout()`
3. **Test isolation**: Each test should be independent
4. **Screenshots on failure**: Enabled by default in config
5. **Parallel execution**: Configure workers for faster tests
6. **Mock external APIs**: Use route interception to avoid flaky tests
7. **Visual regression**: Take screenshots and compare for UI changes
8. **Accessibility**: Include a11y testing in your suite

## 🤝 Contributing

To add new examples:

1. Create test file in `tests/` directory
2. Use descriptive test names
3. Add comments explaining test logic
4. Include error handling
5. Update this README

## 📝 License

These examples are provided as-is for educational purposes.
