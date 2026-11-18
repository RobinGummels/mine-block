import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 45 * 60 * 1000,
  expect: { timeout: 45 * 60 * 1000 },
  workers: 1,
  retries: 0,
  outputDir: '../.runtime/playwright-results',
  reporter: [['list'], ['html', { outputFolder: '../.runtime/playwright-report', open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:6001',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File ../scripts/start-storybook.ps1',
    url: 'http://127.0.0.1:6001/index.json',
    reuseExistingServer: true,
    timeout: 20 * 60 * 1000,
  },
});
