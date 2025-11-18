/**
 * Global Setup
 * Runs once before all tests
 */

const fs = require('fs');
const path = require('path');

async function globalSetup(config) {
  console.log('\n🚀 Starting UI Test Suite Setup...\n');

  // Create necessary directories
  const dirs = [
    'test-results',
    'test-results/screenshots',
    'test-results/videos',
    'test-results/traces',
    'test-results/artifacts',
    'test-results/html-report'
  ];

  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`✅ Created directory: ${dir}`);
    }
  });

  // Log environment information
  console.log('\n📋 Test Environment:');
  console.log(`   Node Version: ${process.version}`);
  console.log(`   Platform: ${process.platform}`);
  console.log(`   Base URL: ${config.use.baseURL}`);
  console.log(`   Parallel Workers: ${config.workers || 'auto'}`);
  console.log(`   Retries: ${config.retries}`);

  // You can add authentication setup here
  // For example, login once and save auth state
  // const { chromium } = require('@playwright/test');
  // const browser = await chromium.launch();
  // const page = await browser.newPage();
  // await page.goto('https://example.com/login');
  // await page.fill('#username', 'test');
  // await page.fill('#password', 'test');
  // await page.click('button[type="submit"]');
  // await page.context().storageState({ path: 'auth.json' });
  // await browser.close();

  console.log('\n✨ Setup complete!\n');
}

module.exports = globalSetup;
