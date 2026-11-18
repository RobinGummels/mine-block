// Render the editable SVG sources with the project's existing Playwright install.
import { readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from '../../qa/node_modules/playwright/index.mjs';

const directory = dirname(fileURLToPath(import.meta.url));
const sources = (await readdir(directory)).filter((name) => name.endsWith('.svg'));
if (sources.length !== 15) throw new Error(`Expected 15 SVG sources, found ${sources.length}`);

const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  for (const name of sources) {
    const width = name === 'cave_background.svg' ? 1920 : 512;
    const height = name === 'cave_background.svg' ? 1080 : name === 'cave_explorer.svg' ? 768 : 512;
    const source = await readFile(join(directory, name), 'utf8');
    const encoded = await page.evaluate(async ({ source, width, height }) => {
      const image = new Image();
      image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(source)}`;
      await image.decode();
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext('2d');
      context.imageSmoothingEnabled = false;
      context.drawImage(image, 0, 0, width, height);
      return canvas.toDataURL('image/png').split(',')[1];
    }, { source, width, height });
    const png = Buffer.from(encoded, 'base64');
    if (png.readUInt32BE(16) !== width || png.readUInt32BE(20) !== height) {
      throw new Error(`Wrong PNG dimensions for ${name}`);
    }
    await writeFile(join(directory, name.replace(/\.svg$/, '.png')), png);
  }

  await page.goto(pathToFileURL(join(directory, 'preview.html')).href);
  await page.locator('.sheet img').last().waitFor();
  await page.screenshot({ path: join(directory, 'preview.png'), fullPage: true });
  await page.locator('.mini').screenshot({ path: join(directory, 'preview-mini.png') });
  await page.locator('.desktop').screenshot({ path: join(directory, 'preview-desktop.png') });
  console.log(`Exported ${sources.length} PNG assets and three previews.`);
} finally {
  await browser.close();
}
