import { test, expect } from '@playwright/test';

for (const viewport of [{width: 1200, height: 675}, {width: 400, height: 225}]) {
  test(`official Lines example ${viewport.width}x${viewport.height}`, async ({page}, testInfo) => {
    const issues = [];
    page.on('pageerror', error => issues.push(`JavaScript: ${error.message}`));
    page.on('requestfailed', request => {
      if (request.failure()?.errorText !== 'net::ERR_ABORTED') {
        issues.push(`Request: ${request.url()} ${request.failure()?.errorText}`);
      }
    });
    page.on('response', response => {
      if (response.status() >= 400) issues.push(`HTTP ${response.status()}: ${response.url()}`);
    });
    page.on('console', message => {
      // The SDK falls back when its optional Adobe Typekit font is inactive on localhost.
      if (message.type() === 'error' && message.text() !== 'Web font load inactive') issues.push(`Console: ${message.text()}`);
    });
    await page.setViewportSize({width: 1440, height: 900});
    await page.goto('/?path=/story/mode-base-book--random');
    const storyLink = page.locator('a[href*="mode-base-book--random"]').first();
    await expect(storyLink).toBeVisible();
    await storyLink.click();
    // Verify the isolated scene at the required embed size as well.
    await page.setViewportSize(viewport);
    await page.goto('/iframe.html?id=mode-base-book--random&viewMode=story');
    const action = page.getByRole('button', {name: 'Action', exact: true});
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();
    await expect(action).toBeEnabled();
    const canvasSize = await canvas.evaluate(node => ({width: node.width, height: node.height}));
    expect(canvasSize.width).toBeGreaterThan(0);
    expect(canvasSize.height).toBeGreaterThan(0);
    await page.screenshot({path: testInfo.outputPath('before-action.png')});
    await action.click();
    await expect(page.getByText('Action is resolved', {exact: false})).toBeVisible({timeout: 120000});
    await expect(action).toBeEnabled();
    await page.screenshot({path: testInfo.outputPath('after-action.png')});
    await testInfo.attach('browser-issues', {body: JSON.stringify(issues, null, 2), contentType: 'application/json'});
    expect(issues).toEqual([]);
  });
}
