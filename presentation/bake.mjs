// 烘焙管線：以真 Kit 渲染母版，@2x 截圖。
// chrome 類（hideText: true）會先隱藏 .ppt-text —— 文字由 PPT 文字框承載。
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { mkdirSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const HERE = dirname(new URL(import.meta.url).pathname);

const JOBS = [
  { file: 'masters/bg.html', out: 'assets/backgrounds/bg-dark.png' },
  { file: 'masters/_calibration.html', out: 'assets/calibration/card.png' },
  { file: 'masters/01-cover.html', out: 'assets/chrome/cover.png', hideText: true },
  { file: 'masters/02-outline.html', out: 'assets/chrome/outline.png', hideText: true },
  { file: 'masters/08-atmosphere.html', out: 'assets/chrome/atmosphere.png', hideText: true },
];

const REFERENCE = [
  '01-cover', '02-outline', '03-pipeline', '04-content', '05-stats',
  '06-table', '07-compare', '08-atmosphere', '09-closing',
].map((n) => ({ file: `masters/${n}.html`, out: `assets/reference/${n}.png` }));

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 2,
});

for (const job of [...JOBS, ...REFERENCE]) {
  const src = resolve(HERE, job.file);
  if (!existsSync(src)) { console.log(`skip（尚未建立）: ${job.file}`); continue; }
  mkdirSync(dirname(resolve(HERE, job.out)), { recursive: true });
  await page.goto(pathToFileURL(src).href);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500); // Kit init 與 glow 靜定
  if (job.hideText) {
    await page.addStyleTag({ content: '.ppt-text { visibility: hidden !important; }' });
  }
  await page.screenshot({ path: resolve(HERE, job.out), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
  console.log(`baked: ${job.out}`);
}
await browser.close();
