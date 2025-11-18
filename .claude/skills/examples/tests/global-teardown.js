/**
 * Global Teardown
 * Runs once after all tests
 */

const fs = require('fs');
const path = require('path');

async function globalTeardown(config) {
  console.log('\n🧹 Running Test Suite Cleanup...\n');

  // Clean up temporary files
  const tempFiles = [
    'auth.json',
    '.temp'
  ];

  tempFiles.forEach(file => {
    if (fs.existsSync(file)) {
      fs.unlinkSync(file);
      console.log(`🗑️  Removed: ${file}`);
    }
  });

  // Generate summary
  const resultsPath = path.join('test-results', 'results.json');
  if (fs.existsSync(resultsPath)) {
    const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));

    console.log('\n📊 Test Summary:');
    console.log(`   Total Tests: ${results.suites?.[0]?.specs?.length || 0}`);
    console.log(`   Duration: ${(results.duration / 1000).toFixed(2)}s`);
  }

  console.log('\n✅ Cleanup complete!\n');
}

module.exports = globalTeardown;
