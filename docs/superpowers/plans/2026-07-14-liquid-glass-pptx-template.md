# Liquid Glass PowerPoint 模板（presentation/）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 UI-ToolBox 建 `presentation/` 子專案，產出一份視覺與 Liquid Glass Kit 同源、可在 PowerPoint 直接編輯的深色 .pptx 模板（9 版面配置 + 元件庫頁 + 範例頁 + 動態波浪背景）。

**Architecture:** 三段管線：`media.sh`（ffmpeg 處理背景影片）→ `bake.mjs`（Playwright 以真 Kit 渲染母版 HTML、@2x 截圖烘焙底圖）→ `build_pptx.py`（python-pptx + lxml 從 `skeleton.pptx` 組裝 theme、slideLayout XML、原生玻璃形狀與範例頁）。母版 HTML 是視覺單一真相；PPT 幾何的單一真相是 `builder/layouts_spec.py`。

**Tech Stack:** Playwright(Chromium, 僅 presentation/ 內 devDependency)、ffmpeg(已裝於 /opt/homebrew)、python-pptx 1.0.2、lxml(隨 python-pptx)、pytest。

**Spec:** `docs/superpowers/specs/2026-07-14-liquid-glass-pptx-template-design.md`。
結構微調（不改 spec 意圖）：`build_pptx.py` 為 CLI 入口，實作拆進 `presentation/builder/` package（theme/layouts/shapes/content 各一檔，單一職責）；`skeleton.pptx` 由 `make_skeleton.py` 產生後進版控。

## Global Constraints

- 工作 repo：`/Users/charles88/Desktop/UI-ToolBox`（以下相對路徑皆以此為根）。
- UI-ToolBox 鐵律：不碰 `site.src.html`、`SPEC.md`、`build_site.py`、`index.html`；絕不執行 `assemble_*.py`。
- Kit 兩檔（`liquid-glass.css/js`）唯讀，母版只以 `../../liquid-glass.css` 相對路徑引用；玻璃一律用 Kit class（`lg lg-card` / `lg lg-static`），**禁止手寫 `backdrop-filter`**。
- 玻璃只做容器：數字、圖表、文字是實心內容層。
- Node 依賴只准出現在 `presentation/package.json`；`presentation/node_modules/` 進 `.gitignore`。Kit 本體維持零依賴宣稱。
- 深色 tokens 固定值：bg `#070B11`、surface `#0D1520`、text `#F5F7FA`、text-dim `#9FB0C0`、hairline 白 10%、accent1 `#35E0A6`、accent2 `#38BDF8`、accent3 `#E9BC63`、accent4 `#F0648C`、accent5 `#7FB4FF`、accent6 `#F5A54A`；字型 Inter / Noto Sans TC / Geist Mono。
- 投影可讀性下限：範例頁與元件內文 ≥ 24pt（PPT 端），發光/亮色只給 KPI 數字與強調。
- 影片來源唯讀：`../iMarine-Carbon-Tokenization-POC/BG_Video/wave.mp4`，複製進 `presentation/assets/media/` 後只處理副本。
- 文件與註解：繁體中文 + 英文術語；**禁止 emoji**；commit 訊息不加任何 AI 署名（無 Co-Authored-By）。
- Python 一律 `python3`（3.10，python-pptx 1.0.2 已裝）；pytest 於 Task 1 安裝。
- 測試指令統一：`cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests -v`。
- 幾何換算：投影片 12192000 x 6858000 EMU（16:9）；母版畫布 1920x1080px；**1px = 6350 EMU**（常數 `PX`）。字級 `a:defRPr sz` 為 pt 的百分之一（5400 = 54pt）。

---

### Task 1: 腳手架 — tokens、theme-dark.css、pytest、playwright

**Files:**
- Create: `presentation/tokens.json`
- Create: `presentation/masters/theme-dark.css`
- Create: `presentation/package.json`
- Create: `presentation/tests/test_tokens.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `tokens.json`（後續所有 Python 讀它）；CSS 變數 `--bg/--surface/--text/--text-dim/--hairline/--accent1..6/--font-*`（後續所有母版讀它）。

- [ ] **Step 1: 寫 tokens.json**

```json
{
  "theme": "dark",
  "bg": "070B11",
  "surface": "0D1520",
  "text": "F5F7FA",
  "textDim": "9FB0C0",
  "hairlineAlpha": 10,
  "accent1": "35E0A6",
  "accent2": "38BDF8",
  "accent3": "E9BC63",
  "accent4": "F0648C",
  "accent5": "7FB4FF",
  "accent6": "F5A54A",
  "fontLatin": "Inter",
  "fontEastAsian": "Noto Sans TC",
  "fontMono": "Geist Mono",
  "card": { "fill": "0D1520", "fillAlpha": 55, "lineAlpha": 12, "radius": 0.06 }
}
```

- [ ] **Step 2: 寫 masters/theme-dark.css（與 tokens.json 同值，測試會驗同步）**

```css
/* 深色主題 tokens —— 與 ../tokens.json 同步，改值兩邊都要改（tests/test_tokens.py 把關） */
:root {
  --bg: #070B11;
  --surface: #0D1520;
  --text: #F5F7FA;
  --text-dim: #9FB0C0;
  --hairline: rgba(255, 255, 255, .10);
  --accent1: #35E0A6;
  --accent2: #38BDF8;
  --accent3: #E9BC63;
  --accent4: #F0648C;
  --accent5: #7FB4FF;
  --accent6: #F5A54A;
  --font-latin: 'Inter';
  --font-ea: 'Noto Sans TC';
  --font-mono: 'Geist Mono';
}
```

- [ ] **Step 3: 寫失敗測試 tests/test_tokens.py**

```python
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_css_tokens_match_json():
    tokens = json.loads((ROOT / "tokens.json").read_text())
    css = (ROOT / "masters" / "theme-dark.css").read_text()
    for key in ["bg", "surface", "text", "textDim"] + [f"accent{i}" for i in range(1, 7)]:
        css_var = {"textDim": "text-dim"}.get(key, key)
        m = re.search(rf"--{css_var}:\s*#([0-9A-Fa-f]{{6}})", css)
        assert m, f"theme-dark.css 缺 --{css_var}"
        assert m.group(1).upper() == tokens[key].upper(), f"--{css_var} 與 tokens.json 不一致"
    assert f'--hairline: rgba(255, 255, 255, .{tokens["hairlineAlpha"]:02d})' in css
```

- [ ] **Step 4: 安裝 pytest 並跑測試確認通過**

```bash
python3 -m pip install --user pytest
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests -v
```
Expected: `test_css_tokens_match_json PASSED`（先寫檔後寫測試，此處直接綠燈即可；若紅燈表示兩檔不同步，修到綠）。

- [ ] **Step 5: 建 package.json 並安裝 playwright（僅 presentation/ 內）**

```json
{
  "name": "liquid-glass-presentation",
  "private": true,
  "type": "module",
  "devDependencies": {
    "playwright": "^1.49.0"
  }
}
```

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && npm install && npx playwright install chromium
```
Expected: `node_modules/` 只出現在 presentation/ 內；chromium 下載完成。

- [ ] **Step 6: .gitignore 追加（保留原有內容，檔尾加）**

```gitignore
# presentation/ 子專案
presentation/node_modules/
presentation/dist/
presentation/assets/media/wave.mp4
```
（`wave.mp4` 原始副本不進 repo；處理後的 loop 產物與烘圖進 repo。）

- [ ] **Step 7: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/ .gitignore && git commit -m "feat(presentation): 腳手架 tokens/theme-dark/package.json 與 tokens 同步測試"
```

---

### Task 2: media.sh — 背景影片三產物

**Files:**
- Create: `presentation/media.sh`
- Test: 人工核對輸出檔存在與大小（shell 產物，無 pytest）

**Interfaces:**
- Produces: `assets/media/wave-loop.mp4`（範例頁動態層）、`assets/media/wave-loop.gif`（備援動態層）、`assets/media/wave-frame.png`（母版靜態波浪原料）。

- [ ] **Step 1: 寫 media.sh**

```bash
#!/usr/bin/env bash
# 背景影片處理：來源唯讀，複製副本後產出 mp4 loop / gif loop / 靜態首幀
set -euo pipefail
cd "$(dirname "$0")"
SRC="../../iMarine-Carbon-Tokenization-POC/BG_Video/wave.mp4"
OUT="assets/media"
mkdir -p "$OUT"
[ -f "$OUT/wave.mp4" ] || cp "$SRC" "$OUT/wave.mp4"

# 1) 無縫循環 mp4：前 9 秒為主體，最後 1 秒與開頭交叉淡接
ffmpeg -y -i "$OUT/wave.mp4" -filter_complex \
  "[0:v]split[a][b];[a]trim=0:9,setpts=PTS-STARTPTS[a1];[b]trim=9:10,setpts=PTS-STARTPTS[b1];[b1][a1]xfade=transition=fade:duration=1:offset=0[v]" \
  -map "[v]" -an -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p "$OUT/wave-loop.mp4"

# 2) GIF：12fps、寬 960、diff palette + bayer 抖色壓 banding
ffmpeg -y -i "$OUT/wave-loop.mp4" -vf \
  "fps=12,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  -loop 0 "$OUT/wave-loop.gif"

# 3) 靜態首幀：第 0 秒幀放大至 1920x1080
ffmpeg -y -i "$OUT/wave.mp4" -vf "select=eq(n\,0),scale=1920:1080" -frames:v 1 "$OUT/wave-frame.png"

ls -lh "$OUT"
```

- [ ] **Step 2: 執行並核對**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && chmod +x media.sh && ./media.sh
```
Expected: 三檔皆存在；`wave-loop.mp4` 約 1–2MB、`wave-frame.png` 為 1920x1080。把三檔實際大小記進 commit 訊息（GIF 大小是 owner 要的資訊）。

- [ ] **Step 3: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/media.sh presentation/assets/media && git commit -m "feat(presentation): media.sh 產出 wave loop mp4/gif 與靜態首幀（mp4 X.XMB / gif X.XMB）"
```

---

### Task 3: deck.css + 背景母版 bg.html + 校準母版 _calibration.html

**Files:**
- Create: `presentation/masters/deck.css`
- Create: `presentation/masters/bg.html`
- Create: `presentation/masters/_calibration.html`

**Interfaces:**
- Produces: 所有母版共用的 `.slide/.bg-layer/.glow/.wave/.eyebrow/.title/.kpi-*/.note-bar/.footer/.ppt-text` class；`bg.html`（乾淨背景）與 `_calibration.html`（單卡特寫）供 Task 4 烘焙。

- [ ] **Step 1: 寫 masters/deck.css**

```css
/* 簡報畫布與排版 primitives —— 玻璃一律用 Kit class，此檔不寫任何 backdrop-filter */
html, body { margin: 0; background: #000; }
.slide {
  position: relative; width: 1920px; height: 1080px; overflow: hidden;
  background: var(--bg); color: var(--text);
  font-family: var(--font-latin), var(--font-ea), sans-serif;
}
.bg-layer { position: absolute; inset: 0; }
.glow { position: absolute; border-radius: 50%; filter: blur(140px); }
.wave {
  position: absolute; left: 0; right: 0; bottom: 0; width: 100%; height: 40%;
  object-fit: cover; opacity: .5;
  -webkit-mask-image: linear-gradient(to top, #000 55%, transparent);
  mask-image: linear-gradient(to top, #000 55%, transparent);
}
.content { position: absolute; inset: 0; padding: 56px 96px; box-sizing: border-box; }
.eyebrow {
  font-size: 22px; font-weight: 600; letter-spacing: .32em;
  text-transform: uppercase; color: var(--accent1);
}
.eyebrow .dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%;
  background: var(--accent1); margin-right: 14px; vertical-align: 1px; }
.title { font-size: 64px; font-weight: 700; line-height: 1.15; margin: 12px 0 0; }
.title-rule { width: 96px; height: 5px; background: var(--accent1); border-radius: 3px; margin-top: 20px; }
.subtitle { font-size: 30px; color: var(--text-dim); font-weight: 400; }
.kpi-num { font-family: var(--font-mono), monospace; font-size: 56px; font-weight: 600; color: var(--accent1); }
.kpi-label { font-size: 22px; color: var(--text-dim); margin-top: 6px; }
.note-bar { display: flex; align-items: center; gap: 20px; padding: 22px 28px; border-radius: 16px; }
.note-bar .tag { color: var(--accent1); font-weight: 700; font-size: 24px; white-space: nowrap; }
.note-bar .txt { font-size: 24px; color: var(--text); }
.footer {
  position: absolute; left: 96px; right: 96px; bottom: 28px;
  display: flex; justify-content: space-between;
  font-size: 18px; color: var(--text-dim);
}
.card-pad { padding: 32px; box-sizing: border-box; border-radius: 20px; }
.row { display: flex; gap: 24px; }
.col { display: flex; flex-direction: column; gap: 24px; }
/* .ppt-text：烘 chrome 時由 bake.mjs 隱藏（文字改由 PPT 文字框承載），平時可見供對位 */
.ppt-text {}
```

- [ ] **Step 2: 寫 masters/bg.html（乾淨背景 = 深底 + 光暈 + 靜態波浪）**

```html
<!doctype html>
<html lang="zh-Hant" data-lg-theme="dark">
<head>
<meta charset="utf-8">
<title>bg</title>
<link rel="stylesheet" href="theme-dark.css">
<link rel="stylesheet" href="deck.css">
</head>
<body>
<div class="slide">
  <div class="bg-layer">
    <div class="glow" style="left:-200px; top:-260px; width:900px; height:700px; background:#12354a; opacity:.55"></div>
    <div class="glow" style="right:-260px; top:120px; width:800px; height:640px; background:#0d3b31; opacity:.45"></div>
    <img class="wave" src="../assets/media/wave-frame.png" alt="">
  </div>
</div>
</body>
</html>
```

- [ ] **Step 3: 寫 masters/_calibration.html（Kit 玻璃卡特寫，供原生形狀配方比對）**

```html
<!doctype html>
<html lang="zh-Hant" data-lg-theme="dark">
<head>
<meta charset="utf-8">
<title>calibration</title>
<link rel="stylesheet" href="../../liquid-glass.css">
<link rel="stylesheet" href="theme-dark.css">
<link rel="stylesheet" href="deck.css">
</head>
<body>
<div class="slide">
  <div class="bg-layer">
    <div class="glow" style="left:-200px; top:-260px; width:900px; height:700px; background:#12354a; opacity:.55"></div>
    <div class="glow" style="right:-260px; top:120px; width:800px; height:640px; background:#0d3b31; opacity:.45"></div>
    <img class="wave" src="../assets/media/wave-frame.png" alt="">
  </div>
  <div class="content" style="display:flex; align-items:center; justify-content:center;">
    <div class="lg lg-card card-pad" data-lg style="width:560px; height:360px;">
      <div class="kpi-num">1,728 萬次</div>
      <div class="kpi-label">Kit 玻璃卡（校準基準）</div>
    </div>
  </div>
  <script src="../../liquid-glass.js"></script>
  <script>LiquidGlass.init();</script>
</div>
</body>
</html>
```

- [ ] **Step 4: 目視檢查**

```bash
open /Users/charles88/Desktop/UI-ToolBox/presentation/masters/_calibration.html
```
Expected: 深底、雙光暈、底部靜態波浪、置中一張 Kit 玻璃卡。

- [ ] **Step 5: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/masters && git commit -m "feat(presentation): deck.css 與 bg/_calibration 母版"
```

---

### Task 4: bake.mjs — Playwright 烘焙管線跑通

**Files:**
- Create: `presentation/bake.mjs`

**Interfaces:**
- Produces: `assets/backgrounds/bg-dark.png`（3840x2160）、`assets/calibration/card.png`、（Task 5 起）`assets/chrome/{cover,outline,atmosphere}.png`、`assets/reference/*.png`。
- Consumes: `masters/*.html`。

- [ ] **Step 1: 寫 bake.mjs**

```js
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
```

- [ ] **Step 2: 執行（此時只有 bg 與 calibration 存在，其餘 skip）**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && node bake.mjs
```
Expected: `baked: assets/backgrounds/bg-dark.png`、`baked: assets/calibration/card.png`，其餘列 skip。

- [ ] **Step 3: 驗尺寸**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && python3 -c "
from PIL import Image
for p in ['assets/backgrounds/bg-dark.png', 'assets/calibration/card.png']:
    print(p, Image.open(p).size)"
```
Expected: 兩張皆 `(3840, 2160)`。

- [ ] **Step 4: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/bake.mjs presentation/assets/backgrounds presentation/assets/calibration && git commit -m "feat(presentation): bake.mjs 烘焙管線與 bg/校準卡底圖"
```

---

### Task 5: 烘焙型母版 — 01-cover / 02-outline / 08-atmosphere

**Files:**
- Create: `presentation/masters/01-cover.html`
- Create: `presentation/masters/02-outline.html`
- Create: `presentation/masters/08-atmosphere.html`

**Interfaces:**
- Produces: `assets/chrome/{cover,outline,atmosphere}.png`（無文字 chrome 底圖）；`.ppt-text` 元素的 px 座標即 Task 8 `layouts_spec.py` 對應 placeholder 的座標來源（下方 HTML 內以 style 標明，抄進 spec 時 1px = 6350 EMU）。

- [ ] **Step 1: 寫 masters/01-cover.html**

```html
<!doctype html>
<html lang="zh-Hant" data-lg-theme="dark">
<head>
<meta charset="utf-8">
<title>cover</title>
<link rel="stylesheet" href="../../liquid-glass.css">
<link rel="stylesheet" href="theme-dark.css">
<link rel="stylesheet" href="deck.css">
</head>
<body>
<div class="slide">
  <div class="bg-layer">
    <div class="glow" style="left:-200px; top:-300px; width:1100px; height:800px; background:#12354a; opacity:.6"></div>
    <div class="glow" style="right:-300px; bottom:-200px; width:1000px; height:760px; background:#0d3b31; opacity:.5"></div>
    <img class="wave" src="../assets/media/wave-frame.png" alt="" style="height:52%; opacity:.65">
  </div>
  <!-- 玻璃主面板（chrome）：文字由 PPT 承載 -->
  <div class="lg lg-card" data-lg style="position:absolute; left:120px; top:300px; width:1160px; height:520px; border-radius:28px;"></div>
  <div class="ppt-text" style="position:absolute; left:180px; top:380px; width:1040px;">
    <div style="font-size:76px; font-weight:700; line-height:1.2;">簡報主標題佔位<br>兩行示意</div>
  </div>
  <div class="ppt-text subtitle" style="position:absolute; left:180px; top:610px; width:1000px;">副標題佔位 · 一行說明</div>
  <div class="title-rule" style="position:absolute; left:180px; top:676px;"></div>
  <div class="ppt-text" style="position:absolute; left:180px; top:716px; width:1000px; font-size:24px; color:var(--text-dim);">作者 / 團隊名稱佔位</div>
  <script src="../../liquid-glass.js"></script>
  <script>LiquidGlass.init();</script>
</div>
</body>
</html>
```

- [ ] **Step 2: 寫 masters/02-outline.html（六張章節卡，卡是 chrome、字是 PPT）**

```html
<!doctype html>
<html lang="zh-Hant" data-lg-theme="dark">
<head>
<meta charset="utf-8">
<title>outline</title>
<link rel="stylesheet" href="../../liquid-glass.css">
<link rel="stylesheet" href="theme-dark.css">
<link rel="stylesheet" href="deck.css">
<style>
  .ocard { position: absolute; width: 544px; height: 300px; border-radius: 20px; }
  .obar { position: absolute; width: 8px; height: 240px; border-radius: 4px; top: 30px; }
</style>
</head>
<body>
<div class="slide">
  <div class="bg-layer">
    <div class="glow" style="left:-200px; top:-260px; width:900px; height:700px; background:#12354a; opacity:.55"></div>
    <div class="glow" style="right:-260px; top:120px; width:800px; height:640px; background:#0d3b31; opacity:.45"></div>
    <img class="wave" src="../assets/media/wave-frame.png" alt="">
  </div>
  <div class="ppt-text" style="position:absolute; left:0; top:70px; width:1920px; text-align:center; font-size:52px; font-weight:700; letter-spacing:.28em;">OUTLINE</div>
  <div style="position:absolute; left:912px; top:150px; width:96px; height:5px; background:var(--accent1); border-radius:3px;"></div>
  <!-- 2x3 卡陣：左上角 (96,220) 起，x 間距 592、y 間距 340 -->
  <div class="lg lg-static ocard" style="left:96px;  top:220px;"><div class="obar" style="left:0; background:var(--accent1)"></div></div>
  <div class="lg lg-static ocard" style="left:688px; top:220px;"><div class="obar" style="left:0; background:var(--accent2)"></div></div>
  <div class="lg lg-static ocard" style="left:1280px;top:220px;"><div class="obar" style="left:0; background:var(--accent3)"></div></div>
  <div class="lg lg-static ocard" style="left:96px;  top:560px;"><div class="obar" style="left:0; background:var(--accent4)"></div></div>
  <div class="lg lg-static ocard" style="left:688px; top:560px;"><div class="obar" style="left:0; background:var(--accent5)"></div></div>
  <div class="lg lg-static ocard" style="left:1280px;top:560px;"><div class="obar" style="left:0; background:var(--accent6)"></div></div>
  <!-- 卡內文字全為 ppt-text（示意一張，其餘由 PPT 範例頁複製） -->
  <div class="ppt-text" style="position:absolute; left:132px; top:250px; width:470px;">
    <div style="font-size:20px; letter-spacing:.3em; color:var(--accent1); font-weight:600;">SECTION 01</div>
    <div style="font-size:36px; font-weight:700; margin-top:10px;">章節標題佔位</div>
    <div style="font-size:22px; color:var(--text-dim); margin-top:14px;">一行章節描述佔位文字</div>
  </div>
  <script src="../../liquid-glass.js"></script>
  <script>LiquidGlass.init();</script>
</div>
</body>
</html>
```

- [ ] **Step 3: 寫 masters/08-atmosphere.html（全幅氛圍頁：滿版波浪 + 底部玻璃標題條）**

```html
<!doctype html>
<html lang="zh-Hant" data-lg-theme="dark">
<head>
<meta charset="utf-8">
<title>atmosphere</title>
<link rel="stylesheet" href="../../liquid-glass.css">
<link rel="stylesheet" href="theme-dark.css">
<link rel="stylesheet" href="deck.css">
</head>
<body>
<div class="slide">
  <div class="bg-layer">
    <img class="wave" src="../assets/media/wave-frame.png" alt=""
         style="height:100%; opacity:.9; -webkit-mask-image:none; mask-image:none;">
    <div style="position:absolute; inset:0; background:linear-gradient(to top, rgba(7,11,17,.85), rgba(7,11,17,.15) 45%);"></div>
  </div>
  <div class="lg lg-card" data-lg style="position:absolute; left:96px; bottom:96px; width:1200px; height:180px; border-radius:24px;"></div>
  <div class="ppt-text" style="position:absolute; left:140px; top:844px; width:1100px; font-size:48px; font-weight:700;">全幅氛圍頁標題佔位</div>
  <script src="../../liquid-glass.js"></script>
  <script>LiquidGlass.init();</script>
</div>
</body>
</html>
```

- [ ] **Step 4: 重烘 + 目視**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && node bake.mjs && open assets/chrome/cover.png assets/chrome/outline.png assets/chrome/atmosphere.png
```
Expected: 三張 chrome 圖 3840x2160、玻璃卡清晰、**無任何文字**（.ppt-text 已隱藏）；assets/reference/ 出現對應含文字版。

- [ ] **Step 5: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/masters presentation/assets && git commit -m "feat(presentation): cover/outline/atmosphere 烘焙型母版與 chrome 底圖"
```

---

### Task 6: 原生參考母版 — 03/04/05/06/07/09

**Files:**
- Create: `presentation/masters/03-pipeline.html`
- Create: `presentation/masters/04-content.html`
- Create: `presentation/masters/05-stats.html`
- Create: `presentation/masters/06-table.html`
- Create: `presentation/masters/07-compare.html`
- Create: `presentation/masters/09-closing.html`

**Interfaces:**
- Produces: `assets/reference/03..09.png`（視覺參考，**不烘 chrome**——這六版型在 PPT 端全用原生形狀重現）；HTML 內 px 座標為 Task 8 幾何來源。

以下六檔共用同一 head 與背景（與 bg.html 相同的 glow + wave），只列 body 主體差異；每檔完整結構 = 下方模板替換 `<!-- BODY -->`：

```html
<!doctype html>
<html lang="zh-Hant" data-lg-theme="dark">
<head>
<meta charset="utf-8">
<title>版型名</title>
<link rel="stylesheet" href="../../liquid-glass.css">
<link rel="stylesheet" href="theme-dark.css">
<link rel="stylesheet" href="deck.css">
</head>
<body>
<div class="slide">
  <div class="bg-layer">
    <div class="glow" style="left:-200px; top:-260px; width:900px; height:700px; background:#12354a; opacity:.55"></div>
    <div class="glow" style="right:-260px; top:120px; width:800px; height:640px; background:#0d3b31; opacity:.45"></div>
    <img class="wave" src="../assets/media/wave-frame.png" alt="">
  </div>
  <!-- BODY -->
  <div class="footer"><span>簡報名稱佔位</span><span>N / 19</span></div>
  <script src="../../liquid-glass.js"></script>
  <script>LiquidGlass.init();</script>
</div>
</body>
</html>
```

- [ ] **Step 1: 03-pipeline.html 的 BODY（標頭 + 五步驟卡 + note bar）**

```html
<div class="content">
  <div class="eyebrow"><span class="dot"></span>OVERVIEW / 章節佔位</div>
  <div class="title">流程 Pipeline 標題佔位</div>
  <div class="title-rule"></div>
</div>
<!-- 五張步驟卡：x = 96 + i*356，w 320、y 300、h 480 -->
<div class="lg lg-static card-pad" style="position:absolute; left:96px;   top:300px; width:320px; height:480px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:452px;  top:300px; width:320px; height:480px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:808px;  top:300px; width:320px; height:480px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:1164px; top:300px; width:320px; height:480px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:1520px; top:300px; width:320px; height:480px;"></div>
<div style="position:absolute; left:96px; top:530px; width:1744px; text-align:center; color:var(--accent1); font-size:34px;">→ 箭頭以 PPT 原生形狀重現 →</div>
<div class="lg lg-static note-bar" style="position:absolute; left:96px; top:860px; width:1728px;">
  <span class="tag">下一步</span><span class="txt">note bar 說明文字佔位，一行結論或補充。</span>
</div>
```

- [ ] **Step 2: 04-content.html 的 BODY（左文字列表 + 右主視覺）**

```html
<div class="content">
  <div class="eyebrow"><span class="dot"></span>01 / SECTION 佔位</div>
  <div class="title">標準內容頁標題佔位</div>
  <div class="title-rule"></div>
</div>
<!-- 左欄三張列表卡 (96,300) w 980，各 h 180、間距 24 -->
<div class="lg lg-static card-pad" style="position:absolute; left:96px; top:300px; width:980px; height:180px;">
  <div style="font-size:30px; font-weight:700;">列表項標題佔位</div>
  <div style="font-size:24px; color:var(--text-dim); margin-top:10px;">兩行說明文字佔位，敘述此列表項的重點內容。</div>
</div>
<div class="lg lg-static card-pad" style="position:absolute; left:96px; top:504px; width:980px; height:180px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:96px; top:708px; width:980px; height:180px;"></div>
<!-- 右主視覺框 (1120,300) 704x588：實心內容層（圖表/圖片不上玻璃） -->
<div style="position:absolute; left:1120px; top:300px; width:704px; height:588px; border:1px solid var(--hairline); border-radius:20px; background:var(--surface); display:flex; align-items:center; justify-content:center; color:var(--text-dim); font-size:26px;">主視覺（圖片 placeholder）</div>
```

- [ ] **Step 3: 05-stats.html 的 BODY（KPI 2x2 + 右主視覺）**

```html
<div class="content">
  <div class="eyebrow"><span class="dot"></span>02 / DATASET 佔位</div>
  <div class="title">統計卡陣列標題佔位</div>
  <div class="title-rule"></div>
</div>
<!-- KPI 2x2：起點 (96,300)，卡 470x270，間距 24 -->
<div class="lg lg-static card-pad" style="position:absolute; left:96px;  top:300px; width:470px; height:270px;">
  <div class="kpi-num">100,000</div><div class="kpi-label">KPI 說明佔位</div>
</div>
<div class="lg lg-static card-pad" style="position:absolute; left:590px; top:300px; width:470px; height:270px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:96px;  top:594px; width:470px; height:270px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:590px; top:594px; width:470px; height:270px;"></div>
<div style="position:absolute; left:1104px; top:300px; width:720px; height:564px; border:1px solid var(--hairline); border-radius:20px; background:var(--surface); display:flex; align-items:center; justify-content:center; color:var(--text-dim); font-size:26px;">主視覺（圖片 placeholder）</div>
<div class="ppt-text" style="position:absolute; left:1104px; top:884px; width:720px; text-align:center; font-size:22px; color:var(--text-dim);">圖說佔位</div>
```

- [ ] **Step 4: 06-table.html 的 BODY（styled 表格示意：表頭 surface、條紋列）**

```html
<div class="content">
  <div class="eyebrow"><span class="dot"></span>04 / RESULT 佔位</div>
  <div class="title">表格頁標題佔位</div>
  <div class="title-rule"></div>
</div>
<div class="lg lg-static" style="position:absolute; left:96px; top:300px; width:1728px; height:600px; border-radius:20px; overflow:hidden;">
  <table style="width:100%; height:100%; border-collapse:collapse; font-size:26px;">
    <tr style="background:rgba(13,21,32,.9); color:var(--accent1); font-weight:700;">
      <td style="padding:20px 28px;">欄位一</td><td>欄位二</td><td>欄位三</td></tr>
    <tr><td style="padding:20px 28px;">內容</td><td>內容</td><td>內容</td></tr>
    <tr style="background:rgba(255,255,255,.06);"><td style="padding:20px 28px;">內容</td><td>內容</td><td>內容</td></tr>
    <tr><td style="padding:20px 28px;">內容</td><td>內容</td><td>內容</td></tr>
  </table>
</div>
```

- [ ] **Step 5: 07-compare.html 的 BODY（三圖並排 + 說明面板）**

```html
<div class="content">
  <div class="eyebrow"><span class="dot"></span>04 / CLUSTERING 佔位</div>
  <div class="title">多圖比較標題佔位</div>
  <div class="title-rule"></div>
</div>
<!-- 三圖框：(96/688/1280, 300) 各 544x460 -->
<div style="position:absolute; left:96px;   top:300px; width:544px; height:460px; border:1px solid var(--hairline); border-radius:20px; background:var(--surface);"></div>
<div style="position:absolute; left:688px;  top:300px; width:544px; height:460px; border:1px solid var(--hairline); border-radius:20px; background:var(--surface);"></div>
<div style="position:absolute; left:1280px; top:300px; width:544px; height:460px; border:1px solid var(--hairline); border-radius:20px; background:var(--surface);"></div>
<div class="lg lg-static note-bar" style="position:absolute; left:96px; top:800px; width:1728px; height:140px;">
  <span class="tag">觀察</span><span class="txt">比較結論說明文字佔位，可寫兩行。</span>
</div>
```

- [ ] **Step 6: 09-closing.html 的 BODY（四張編號結論卡 + Thank You）**

```html
<div class="ppt-text" style="position:absolute; left:0; top:80px; width:1920px; text-align:center; font-size:52px; font-weight:700; letter-spacing:.28em;">CONCLUSION</div>
<div style="position:absolute; left:912px; top:160px; width:96px; height:5px; background:var(--accent1); border-radius:3px;"></div>
<!-- 四卡：x = 96 + i*444，w 420 h 420，y 240 -->
<div class="lg lg-static card-pad" style="position:absolute; left:96px;   top:240px; width:420px; height:420px;">
  <div style="font-family:var(--font-mono); font-size:56px; font-weight:700; color:var(--accent4);">01</div>
  <div style="font-size:30px; font-weight:700; margin-top:16px;">結論標題佔位</div>
  <div style="font-size:24px; color:var(--text-dim); margin-top:12px;">結論描述文字佔位，兩到三行。</div>
</div>
<div class="lg lg-static card-pad" style="position:absolute; left:540px;  top:240px; width:420px; height:420px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:984px;  top:240px; width:420px; height:420px;"></div>
<div class="lg lg-static card-pad" style="position:absolute; left:1428px; top:240px; width:420px; height:420px;"></div>
<div class="ppt-text" style="position:absolute; left:0; top:760px; width:1920px; text-align:center; font-size:64px; font-weight:700; color:var(--accent1);">Thank You</div>
<div class="ppt-text" style="position:absolute; left:0; top:870px; width:1920px; text-align:center; font-size:24px; color:var(--text-dim);">團隊名單佔位</div>
```

- [ ] **Step 7: 重烘 + 目視全部 reference**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && node bake.mjs && open assets/reference
```
Expected: 9 張 reference 圖齊全，版面與上列座標一致。

- [ ] **Step 8: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/masters presentation/assets/reference && git commit -m "feat(presentation): 六支原生參考母版與 reference 烘圖"
```

---

### Task 7: skeleton.pptx 產生器 + theme 寫入

**Files:**
- Create: `presentation/make_skeleton.py`
- Create: `presentation/builder/__init__.py`
- Create: `presentation/builder/theme.py`
- Test: `presentation/tests/test_theme.py`

**Interfaces:**
- Produces: `presentation/skeleton.pptx`（16:9、單一 master、僅一個 Blank layout、master 背景 #070B11）；`builder.theme.write_theme(prs, tokens) -> None`；`builder/__init__.py` 提供 `PX = 6350`、`load_tokens() -> dict`、`ROOT: Path`。
- Consumes: `tokens.json`。

- [ ] **Step 1: builder/__init__.py**

```python
"""presentation builder：從 skeleton.pptx 組裝 Liquid Glass 深色模板。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PX = 6350  # 1 母版 px = 6350 EMU（12192000 / 1920）


def load_tokens() -> dict:
    return json.loads((ROOT / "tokens.json").read_text())
```

- [ ] **Step 2: make_skeleton.py**

```python
"""產生最小 skeleton.pptx：16:9、單 master、僅留 Blank layout、master 背景 #070B11。
執行一次，產物進版控；build_pptx.py 以它為起點。"""
from pptx import Presentation
from pptx.util import Emu
from pptx.oxml.ns import qn
from lxml import etree

NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'


def main():
    prs = Presentation()
    prs.slide_width = Emu(12192000)
    prs.slide_height = Emu(6858000)
    master = prs.slide_masters[0]

    # 只留名為 Blank 的 layout，其餘從 sldLayoutIdLst 與 rels 移除
    id_lst = master.element.find(qn("p:sldLayoutIdLst"))
    for layout in list(master.slide_layouts):
        if layout.name == "Blank":
            continue
        for sld_id in list(id_lst):
            r_id = sld_id.get(qn("r:id"))
            if master.part.related_part(r_id) is layout.part:
                master.part.drop_rel(r_id)
                id_lst.remove(sld_id)
                break

    # master 背景設實心 #070B11（任何縫隙都保持深色）
    bg = etree.fromstring(
        f'<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" {NS}>'
        '<p:bgPr><a:solidFill><a:srgbClr val="070B11"/></a:solidFill>'
        "<a:effectLst/></p:bgPr></p:bg>"
    )
    c_sld = master.element.find(qn("p:cSld"))
    c_sld.insert(0, bg)

    prs.save("skeleton.pptx")
    print("skeleton.pptx 已產生；layouts =", [l.name for l in prs.slide_masters[0].slide_layouts])


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: builder/theme.py**

```python
"""把 tokens 寫進佈景主題：accent1..6 色票與 major/minor 字型。"""
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn


def _theme_element(prs):
    master_part = prs.slide_masters[0].part
    theme_part = master_part.part_related_by(RT.THEME)
    return theme_part._element


def write_theme(prs, tokens: dict) -> None:
    theme = _theme_element(prs)
    scheme = theme.find(qn("a:themeElements")).find(qn("a:clrScheme"))
    for i in range(1, 7):
        node = scheme.find(qn(f"a:accent{i}"))
        for child in list(node):
            node.remove(child)
        srgb = node.makeelement(qn("a:srgbClr"), {"val": tokens[f"accent{i}"]})
        node.append(srgb)

    fonts = theme.find(qn("a:themeElements")).find(qn("a:fontScheme"))
    for tag in ("a:majorFont", "a:minorFont"):
        group = fonts.find(qn(tag))
        group.find(qn("a:latin")).set("typeface", tokens["fontLatin"])
        group.find(qn("a:ea")).set("typeface", tokens["fontEastAsian"])
```

- [ ] **Step 4: 寫失敗測試 tests/test_theme.py**

```python
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def prs():
    import sys
    sys.path.insert(0, str(ROOT))
    from builder import load_tokens
    from builder.theme import write_theme

    p = Presentation(ROOT / "skeleton.pptx")
    write_theme(p, load_tokens())
    return p


def test_skeleton_is_minimal(prs):
    assert prs.slide_width == 12192000 and prs.slide_height == 6858000
    layouts = list(prs.slide_masters[0].slide_layouts)
    assert [l.name for l in layouts] == ["Blank"]


def test_theme_accents_and_fonts(prs):
    theme = prs.slide_masters[0].part.part_related_by(RT.THEME)._element
    scheme = theme.find(qn("a:themeElements")).find(qn("a:clrScheme"))
    assert scheme.find(qn("a:accent1")).find(qn("a:srgbClr")).get("val") == "35E0A6"
    assert scheme.find(qn("a:accent4")).find(qn("a:srgbClr")).get("val") == "F0648C"
    fonts = theme.find(qn("a:themeElements")).find(qn("a:fontScheme"))
    major = fonts.find(qn("a:majorFont"))
    assert major.find(qn("a:latin")).get("typeface") == "Inter"
    assert major.find(qn("a:ea")).get("typeface") == "Noto Sans TC"
```

- [ ] **Step 5: 跑測試確認失敗**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests/test_theme.py -v
```
Expected: FAIL（skeleton.pptx 不存在）。

- [ ] **Step 6: 產生 skeleton 並跑到綠**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && python3 make_skeleton.py
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests/test_theme.py -v
```
Expected: `layouts = ['Blank']`；兩測試 PASS。若 `Blank` 判斷取不到（python-pptx 預設模板 layout 名稱不同），先印 `[l.name for l in master.slide_layouts]` 調整比對字串。

- [ ] **Step 7: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/make_skeleton.py presentation/skeleton.pptx presentation/builder presentation/tests/test_theme.py && git commit -m "feat(presentation): skeleton.pptx 產生器與 theme tokens 寫入"
```

---

### Task 8: layout 引擎 — clone_layout / 背景圖 / placeholder / layouts_spec

**Files:**
- Create: `presentation/builder/layouts.py`
- Create: `presentation/builder/layouts_spec.py`
- Test: `presentation/tests/test_layouts.py`

**Interfaces:**
- Consumes: `builder.PX`、`skeleton.pptx` 的 Blank layout、`assets/backgrounds|chrome/*.png`。
- Produces: `layouts.build_layouts(prs, tokens) -> dict[str, SlideLayout]`（name -> layout proxy）；`layouts_spec.LAYOUTS: list[dict]`，每項 `{name, background, placeholders:[{ph_type, idx, x, y, w, h, sz, b, color, align}]}`（座標單位 px）。

- [ ] **Step 1: builder/layouts_spec.py（PPT 幾何單一真相；座標抄自母版 HTML）**

```python
"""9 個 slide layout 的幾何規格。座標 px（1920x1080 畫布），build 時乘 PX 轉 EMU。
ph_type: 'title' 或 'body'；body 必帶 idx >= 1。color 為 hex 字串。"""

TEXT = "F5F7FA"
DIM = "9FB0C0"

LAYOUTS = [
    {
        "name": "LG 封面",
        "background": "assets/chrome/cover.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 180, "y": 360, "w": 1040, "h": 220, "sz": 54, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 180, "y": 600, "w": 1000, "h": 60, "sz": 22, "b": False, "color": DIM, "align": "l"},
            {"ph_type": "body", "idx": 2, "x": 180, "y": 706, "w": 1000, "h": 50, "sz": 16, "b": False, "color": DIM, "align": "l"},
        ],
    },
    {
        "name": "LG Outline",
        "background": "assets/chrome/outline.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 460, "y": 56, "w": 1000, "h": 90, "sz": 38, "b": True, "color": TEXT, "align": "c"},
        ],
    },
    {
        "name": "LG 流程",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
        ],
    },
    {
        "name": "LG 內容",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
            {"ph_type": "body", "idx": 2, "x": 96, "y": 300, "w": 980, "h": 588, "sz": 18, "b": False, "color": TEXT, "align": "l"},
        ],
    },
    {
        "name": "LG 統計",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
            {"ph_type": "body", "idx": 2, "x": 1104, "y": 884, "w": 720, "h": 50, "sz": 16, "b": False, "color": DIM, "align": "c"},
        ],
    },
    {
        "name": "LG 表格",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
        ],
    },
    {
        "name": "LG 比較",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
        ],
    },
    {
        "name": "LG 氛圍",
        "background": "assets/chrome/atmosphere.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 140, "y": 830, "w": 1100, "h": 120, "sz": 44, "b": True, "color": TEXT, "align": "l"},
        ],
    },
    {
        "name": "LG 結語",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 260, "y": 60, "w": 1400, "h": 100, "sz": 44, "b": True, "color": TEXT, "align": "c"},
            {"ph_type": "body", "idx": 1, "x": 260, "y": 750, "w": 1400, "h": 100, "sz": 44, "b": True, "color": "35E0A6", "align": "c"},
            {"ph_type": "body", "idx": 2, "x": 260, "y": 870, "w": 1400, "h": 50, "sz": 16, "b": False, "color": DIM, "align": "c"},
        ],
    },
]
```

- [ ] **Step 2: 寫失敗測試 tests/test_layouts.py**

```python
import sys
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EXPECTED = ["LG 封面", "LG Outline", "LG 流程", "LG 內容", "LG 統計",
            "LG 表格", "LG 比較", "LG 氛圍", "LG 結語"]


@pytest.fixture(scope="module")
def prs():
    from builder import load_tokens
    from builder.theme import write_theme
    from builder.layouts import build_layouts

    p = Presentation(ROOT / "skeleton.pptx")
    write_theme(p, load_tokens())
    build_layouts(p, load_tokens())
    return p


def test_nine_layouts_created(prs):
    names = [l.name for l in prs.slide_masters[0].slide_layouts]
    for n in EXPECTED:
        assert n in names, f"缺 layout {n}"


def test_layout_backgrounds_are_pictures(prs):
    for layout in prs.slide_masters[0].slide_layouts:
        if layout.name not in EXPECTED:
            continue
        bg = layout.element.find(qn("p:cSld")).find(qn("p:bg"))
        assert bg is not None, f"{layout.name} 無背景"
        blip = bg.find(qn("p:bgPr")).find(qn("a:blipFill")).find(qn("a:blip"))
        r_id = blip.get(qn("r:embed"))
        part = layout.part.related_part(r_id)
        assert part.content_type.startswith("image/"), f"{layout.name} 背景非圖片"


def test_cover_placeholder_geometry(prs):
    cover = next(l for l in prs.slide_masters[0].slide_layouts if l.name == "LG 封面")
    title = next(ph for ph in cover.placeholders if ph.placeholder_format.type is not None
                 and ph.placeholder_format.idx == 0)
    assert title.left == 180 * 6350
    assert title.top == 360 * 6350


def test_roundtrip_save_load(prs, tmp_path):
    out = tmp_path / "t.pptx"
    prs.save(out)
    p2 = Presentation(out)
    assert len(list(p2.slide_masters[0].slide_layouts)) >= 9
```

- [ ] **Step 3: 跑測試確認失敗**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests/test_layouts.py -v
```
Expected: FAIL（`builder.layouts` 不存在）。

- [ ] **Step 4: 寫 builder/layouts.py**

```python
"""slide layout 引擎：clone Blank layout、鋪背景圖、放 placeholder。
python-pptx 公開 API 不支援新建 layout，此處以 part 層 clone + lxml 完成。"""
import copy

from lxml import etree
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.oxml.ns import qn
from pptx.parts.slide import SlideLayoutPart

from . import PX, ROOT

NSMAP = (
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)

ALIGN = {"l": "l", "c": "ctr", "r": "r"}


def _next_layout_partname(package) -> PackURI:
    nums = [
        int(part.partname.filename[len("slideLayout"):-len(".xml")])
        for part in package.iter_parts()
        if str(part.partname).startswith("/ppt/slideLayouts/slideLayout")
    ]
    return PackURI(f"/ppt/slideLayouts/slideLayout{max(nums) + 1}.xml")


def _clone_blank_layout(master, name: str):
    blank = master.slide_layouts[0]
    src_part = blank.part
    package = src_part.package
    el = copy.deepcopy(src_part._element)
    new_part = SlideLayoutPart(_next_layout_partname(package), src_part.content_type, package, el)
    new_part.relate_to(master.part, RT.SLIDE_MASTER)
    r_id = master.part.relate_to(new_part, RT.SLIDE_LAYOUT)

    id_lst = master.element.find(qn("p:sldLayoutIdLst"))
    max_id = max((int(e.get("id")) for e in id_lst), default=2147483648)
    entry = id_lst.makeelement(qn("p:sldLayoutId"), {"id": str(max_id + 1)})
    entry.set(qn("r:id"), r_id)
    id_lst.append(entry)

    el.find(qn("p:cSld")).set("name", name)
    return new_part


def _set_background(layout_part, image_path: str) -> None:
    image_part, r_id = layout_part.get_or_add_image_part(str(ROOT / image_path))
    bg = etree.fromstring(
        f"<p:bg {NSMAP}><p:bgPr><a:blipFill>"
        f'<a:blip r:embed="{r_id}"/><a:stretch><a:fillRect/></a:stretch>'
        "</a:blipFill><a:effectLst/></p:bgPr></p:bg>"
    )
    c_sld = layout_part._element.find(qn("p:cSld"))
    old = c_sld.find(qn("p:bg"))
    if old is not None:
        c_sld.remove(old)
    c_sld.insert(0, bg)


def _add_placeholder(layout_part, spec: dict, sp_id: int, tokens: dict) -> None:
    ph_attr = 'type="title"' if spec["ph_type"] == "title" else f'type="body" idx="{spec["idx"]}"'
    algn = ALIGN[spec.get("align", "l")]
    bold = "1" if spec["b"] else "0"
    sp = etree.fromstring(
        f"<p:sp {NSMAP}>"
        f'<p:nvSpPr><p:cNvPr id="{sp_id}" name="ph{sp_id}"/>'
        '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f"<p:nvPr><p:ph {ph_attr}/></p:nvPr></p:nvSpPr>"
        "<p:spPr><a:xfrm>"
        f'<a:off x="{spec["x"] * PX}" y="{spec["y"] * PX}"/>'
        f'<a:ext cx="{spec["w"] * PX}" cy="{spec["h"] * PX}"/>'
        '</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        '<p:txBody><a:bodyPr/><a:lstStyle>'
        f'<a:lvl1pPr algn="{algn}"><a:defRPr sz="{spec["sz"] * 100}" b="{bold}">'
        f'<a:solidFill><a:srgbClr val="{spec["color"]}"/></a:solidFill>'
        f'<a:latin typeface="{tokens["fontLatin"]}"/><a:ea typeface="{tokens["fontEastAsian"]}"/>'
        "</a:defRPr></a:lvl1pPr></a:lstStyle>"
        "<a:p><a:r><a:t>佔位文字</a:t></a:r></a:p></p:txBody></p:sp>"
    )
    layout_part._element.find(qn("p:cSld")).find(qn("p:spTree")).append(sp)


def build_layouts(prs, tokens: dict) -> dict:
    from .layouts_spec import LAYOUTS

    master = prs.slide_masters[0]
    for spec in LAYOUTS:
        part = _clone_blank_layout(master, spec["name"])
        _set_background(part, spec["background"])
        for i, ph in enumerate(spec["placeholders"]):
            _add_placeholder(part, ph, sp_id=100 + i, tokens=tokens)
    return {l.name: l for l in master.slide_layouts}
```

- [ ] **Step 5: 跑到綠**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests/test_layouts.py presentation/tests/test_theme.py -v
```
Expected: 全 PASS。常見坑：(a) `iter_parts` 需從 `package` 呼叫；(b) title placeholder 的 `placeholder_format.idx` 為 0；(c) `sldLayoutId` 的 id 必須全 presentation 唯一且 >= 2147483648。

- [ ] **Step 6: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/builder presentation/tests/test_layouts.py && git commit -m "feat(presentation): layout 引擎與 9 版型幾何規格"
```

---

### Task 9: 玻璃卡工廠 + 元件庫頁

**Files:**
- Create: `presentation/builder/shapes.py`
- Create: `presentation/builder/components.py`
- Test: `presentation/tests/test_components.py`

**Interfaces:**
- Consumes: `builder.PX`、`load_tokens()`、Task 8 的 `build_layouts`。
- Produces: `shapes.add_glass_card(shapes, x, y, w, h, tokens) -> shape`（px 座標）、`shapes.add_text(shapes, x, y, w, h, text, sz, color, bold=False, mono=False, align='l', tokens=None) -> shape`、`shapes.add_accent_bar(shapes, x, y, w, h, hex_color) -> shape`、`components.add_component_slides(prs, layouts, tokens) -> None`（掛在「LG 內容」layout 上加 2 頁元件庫）。

- [ ] **Step 1: 寫失敗測試 tests/test_components.py**

```python
import sys
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def prs():
    from builder import load_tokens
    from builder.theme import write_theme
    from builder.layouts import build_layouts
    from builder.components import add_component_slides

    p = Presentation(ROOT / "skeleton.pptx")
    tokens = load_tokens()
    write_theme(p, tokens)
    layouts = build_layouts(p, tokens)
    add_component_slides(p, layouts, tokens)
    return p


def test_component_slides_exist(prs):
    assert len(list(prs.slides)) >= 2


def test_glass_card_has_alpha_fill(prs):
    slide = list(prs.slides)[0]
    alphas = slide.shapes._spTree.findall(
        ".//" + qn("a:solidFill") + "/" + qn("a:srgbClr") + "/" + qn("a:alpha"))
    assert alphas, "元件庫頁找不到帶 alpha 的玻璃卡填色"
    assert any(a.get("val") == "55000" for a in alphas)


def test_kpi_number_uses_mono_font(prs):
    slide = list(prs.slides)[0]
    latins = [r.get("typeface") for r in slide.shapes._spTree.iter(qn("a:latin"))]
    assert "Geist Mono" in latins
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests/test_components.py -v
```
Expected: FAIL（`builder.components` 不存在）。

- [ ] **Step 3: 寫 builder/shapes.py**

```python
"""原生玻璃形狀工廠：圓角矩形 + 半透明填色 + 髮絲線 + 柔影。座標一律 px。"""
from lxml import etree
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

from . import PX

A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
_ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}


def _append_alpha(srgb_el, pct: int) -> None:
    srgb_el.append(srgb_el.makeelement(qn("a:alpha"), {"val": str(pct * 1000)}))


def _fill_srgb(shape):
    # 走 spPr 的 XML 路徑，不碰 ColorFormat 私有屬性
    return shape._element.spPr.find(qn("a:solidFill") + "/" + qn("a:srgbClr"))


def add_glass_card(shapes, x, y, w, h, tokens):
    card = tokens["card"]
    sp = shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                          Emu(x * PX), Emu(y * PX), Emu(w * PX), Emu(h * PX))
    sp.adjustments[0] = card["radius"]
    sp.fill.solid()
    sp.fill.fore_color.rgb = RGBColor.from_string(card["fill"])
    _append_alpha(_fill_srgb(sp), card["fillAlpha"])

    sp.line.color.rgb = RGBColor.from_string("FFFFFF")
    sp.line.width = Pt(1)
    ln = sp._element.spPr.find(qn("a:ln"))
    _append_alpha(ln.find(".//" + qn("a:srgbClr")), card["lineAlpha"])

    # 注意：不可先 sp.shadow.inherit = False（會建空 effectLst，再 append 會出現兩個 effectLst，schema 違規）。
    # 直接 append 自己的 effectLst 即同時覆蓋繼承。
    effect = etree.fromstring(
        f"<a:effectLst {A}>"
        '<a:outerShdw blurRad="228600" dist="76200" dir="5400000" rotWithShape="0">'
        '<a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>'
        "</a:outerShdw></a:effectLst>"
    )
    sp._element.spPr.append(effect)
    sp.text_frame.paragraphs[0].text = ""
    return sp


def add_text(shapes, x, y, w, h, text, sz, color, bold=False, mono=False, align="l", tokens=None):
    box = shapes.add_textbox(Emu(x * PX), Emu(y * PX), Emu(w * PX), Emu(h * PX))
    tf = box.text_frame
    tf.word_wrap = True
    para = tf.paragraphs[0]
    para.alignment = _ALIGN[align]
    run = para.add_run()
    run.text = text
    run.font.size = Pt(sz)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = tokens["fontMono"] if mono else tokens["fontLatin"]
    if not mono:
        # East Asian 字型
        rpr = run._r.get_or_add_rPr()
        ea = rpr.makeelement(qn("a:ea"), {"typeface": tokens["fontEastAsian"]})
        rpr.append(ea)
    return box


def add_accent_bar(shapes, x, y, w, h, hex_color):
    sp = shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                          Emu(x * PX), Emu(y * PX), Emu(w * PX), Emu(h * PX))
    sp.adjustments[0] = 0.5
    sp.fill.solid()
    sp.fill.fore_color.rgb = RGBColor.from_string(hex_color)
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp
```

- [ ] **Step 4: 寫 builder/components.py**

```python
"""元件庫頁：KPI 卡、note bar、chip、編號卡、章節 nav 膠囊、styled 表格。全原生形狀。"""
from pptx.dml.color import RGBColor
from pptx.util import Emu, Pt

from . import PX
from .shapes import add_accent_bar, add_glass_card, add_text


def _blank_on(prs, layouts, name):
    slide = prs.slides.add_slide(layouts[name])
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    return slide


def add_component_slides(prs, layouts, tokens) -> None:
    t = tokens
    # --- 元件庫 1：KPI 卡 / note bar / chips / nav 膠囊 ---
    s1 = _blank_on(prs, layouts, "LG 內容")
    add_text(s1.shapes, 96, 40, 900, 50, "元件庫 1 / KPI · note bar · chip · nav", 20, t["textDim"], tokens=t)

    # KPI 卡（玻璃卡 + mono 大數字 + 標籤）
    add_glass_card(s1.shapes, 96, 130, 470, 270, t)
    add_text(s1.shapes, 128, 170, 400, 90, "1,728 萬", 40, t["accent1"], bold=True, mono=True, tokens=t)
    add_text(s1.shapes, 128, 290, 400, 50, "KPI 標籤文字", 16, t["textDim"], tokens=t)

    # note bar（玻璃長條 + accent 左標）
    add_glass_card(s1.shapes, 96, 460, 1728, 110, t)
    add_accent_bar(s1.shapes, 120, 484, 8, 62, t["accent1"])
    add_text(s1.shapes, 156, 486, 120, 50, "結論", 18, t["accent1"], bold=True, tokens=t)
    add_text(s1.shapes, 290, 486, 1480, 60, "note bar 說明文字：一行重點結論或補充。", 18, t["text"], tokens=t)

    # chips（三個小膠囊）
    for i, (label, color) in enumerate([("LIVE", t["accent1"]), ("MOCK", t["accent3"]), ("ALERT", t["accent4"])]):
        x = 96 + i * 220
        card = add_glass_card(s1.shapes, x, 640, 180, 64, t)
        card.adjustments[0] = 0.5
        add_text(s1.shapes, x, 652, 180, 40, label, 14, color, bold=True, align="c", tokens=t)

    # 章節 nav 膠囊列（六格）
    for i in range(6):
        x = 96 + i * 300
        card = add_glass_card(s1.shapes, x, 780, 280, 70, t)
        card.adjustments[0] = 0.5
        add_text(s1.shapes, x, 796, 280, 40, f"Section {i + 1}", 14, t["text"], align="c", tokens=t)

    # --- 元件庫 2：編號卡 / styled 表格 ---
    s2 = _blank_on(prs, layouts, "LG 內容")
    add_text(s2.shapes, 96, 40, 900, 50, "元件庫 2 / 編號卡 · 表格", 20, t["textDim"], tokens=t)

    add_glass_card(s2.shapes, 96, 130, 420, 420, t)
    add_text(s2.shapes, 128, 160, 200, 90, "01", 40, t["accent4"], bold=True, mono=True, tokens=t)
    add_text(s2.shapes, 128, 280, 360, 60, "編號卡標題", 22, t["text"], bold=True, tokens=t)
    add_text(s2.shapes, 128, 350, 360, 140, "編號卡描述文字，兩到三行的說明內容。", 16, t["textDim"], tokens=t)

    # styled 表格：表頭 surface 填色 + accent 字、條紋列
    rows, cols = 4, 3
    gf = s2.shapes.add_table(rows, cols, Emu(600 * PX), Emu(130 * PX), Emu(1220 * PX), Emu(420 * PX))
    table = gf.table
    for c in range(cols):
        cell = table.cell(0, c)
        cell.text = f"欄位{c + 1}"
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor.from_string(t["surface"])
        para = cell.text_frame.paragraphs[0]
        para.runs[0].font.color.rgb = RGBColor.from_string(t["accent1"])
        para.runs[0].font.bold = True
        para.runs[0].font.size = Pt(16)
    for r in range(1, rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = "內容"
            cell.fill.solid()
            shade = "10141B" if r % 2 else "0B111A"
            cell.fill.fore_color.rgb = RGBColor.from_string(shade)
            para = cell.text_frame.paragraphs[0]
            para.runs[0].font.color.rgb = RGBColor.from_string(t["text"])
            para.runs[0].font.size = Pt(14)
```

- [ ] **Step 5: 跑到綠**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests/test_components.py -v
```
Expected: 3 測試 PASS。若 `test_component_slides_exist` 的內部屬性寫法出錯，改為 `assert len(list(prs.slides)) >= 2` 單一斷言即可。

- [ ] **Step 6: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/builder presentation/tests/test_components.py && git commit -m "feat(presentation): 玻璃形狀工廠與元件庫頁"
```

---

### Task 10: 範例頁 + 動態背景嵌入 + build_pptx.py CLI

**Files:**
- Create: `presentation/builder/content.py`
- Create: `presentation/build_pptx.py`
- Test: `presentation/tests/test_examples.py`

**Interfaces:**
- Consumes: Task 7–9 全部；`assets/media/wave-loop.mp4`、`assets/media/wave-frame.png`。
- Produces: `content.add_example_slides(prs, layouts, tokens) -> None`（9 頁範例，每頁最底層動態 mp4）；`content.add_bg_movie(slide, prs) -> None`；CLI `python3 build_pptx.py [--calibration] [-o 路徑]` 產出 `dist/liquid-glass-dark.pptx`。

- [ ] **Step 1: 寫失敗測試 tests/test_examples.py**

```python
import sys
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def dist(tmp_path_factory):
    sys.path.insert(0, str(ROOT))
    import build_pptx

    out = tmp_path_factory.mktemp("dist") / "t.pptx"
    build_pptx.build(out, calibration=False)
    return out


def test_build_produces_file(dist):
    assert dist.exists() and dist.stat().st_size > 0


def test_example_slides_use_all_nine_layouts(dist):
    prs = Presentation(dist)
    used = {s.slide_layout.name for s in prs.slides}
    for n in ["LG 封面", "LG Outline", "LG 流程", "LG 內容", "LG 統計",
              "LG 表格", "LG 比較", "LG 氛圍", "LG 結語"]:
        assert n in used, f"範例頁缺 {n}"


def test_movie_embedded_and_autoplay(dist):
    prs = Presentation(dist)
    cover = next(s for s in prs.slides if s.slide_layout.name == "LG 封面")
    videos = cover._element.findall(".//" + qn("a:videoFile"))
    assert videos, "封面範例頁沒有影片"
    timing = cover._element.find(qn("p:timing"))
    conds = [c.get("delay") for c in timing.iter(qn("p:cond"))]
    assert "indefinite" not in conds, "影片仍是點擊播放（delay=indefinite 未改 0）"
    ctns = [c.get("repeatCount") for c in timing.iter(qn("p:cTn"))]
    assert "indefinite" in ctns, "影片未設 loop"


def test_file_size_sane(dist):
    assert dist.stat().st_size < 60 * 1024 * 1024, "產物超過 60MB，媒體疑似未去重"
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests/test_examples.py -v
```
Expected: FAIL（`build_pptx` 無 `build`）。

- [ ] **Step 3: 寫 builder/content.py**

```python
"""範例頁：每版型一頁假內容，最底層埋動態 mp4（autoplay + loop）。"""
from pptx.oxml.ns import qn
from pptx.util import Emu

from . import PX, ROOT
from .shapes import add_accent_bar, add_glass_card, add_text

MP4 = ROOT / "assets" / "media" / "wave-loop.mp4"
POSTER = ROOT / "assets" / "media" / "wave-frame.png"


def add_bg_movie(slide, prs) -> None:
    movie = slide.shapes.add_movie(
        str(MP4), 0, 0, prs.slide_width, prs.slide_height,
        poster_frame_image=str(POSTER), mime_type="video/mp4")
    # 移到最底層（spTree 前兩個子節點是 nvGrpSpPr/grpSpPr）
    el = movie._element
    tree = el.getparent()
    tree.remove(el)
    tree.insert(2, el)
    # autoplay：click 觸發的 delay=indefinite 改 0
    timing = slide._element.find(qn("p:timing"))
    for cond in timing.iter(qn("p:cond")):
        if cond.get("delay") == "indefinite":
            cond.set("delay", "0")
    # loop：cMediaNode 的 cTn 設 repeatCount
    for cmed in timing.iter(qn("p:cMediaNode")):
        ctn = cmed.find(qn("p:cTn"))
        if ctn is not None:
            ctn.set("repeatCount", "indefinite")


def _fill_placeholders(slide, texts: dict) -> None:
    for ph in slide.placeholders:
        idx = ph.placeholder_format.idx
        if idx in texts:
            ph.text = texts[idx]


def add_example_slides(prs, layouts, tokens) -> None:
    t = tokens
    # 每版型一頁；title 的 idx 為 0
    plan = [
        ("LG 封面", {0: "永續智能航港生態系", 1: "Liquid Glass 深色簡報模板 範例", 2: "團隊名稱 · 2026"}),
        ("LG Outline", {0: "OUTLINE"}),
        ("LG 流程", {0: "研究流程 Pipeline", 1: "OVERVIEW / 研究脈絡"}),
        ("LG 內容", {0: "標準內容頁標題", 1: "01 / MOTIVATION",
                     2: "左欄內容文字範例：\n重點一說明\n重點二說明\n重點三說明"}),
        ("LG 統計", {0: "資料集統計", 1: "02 / DATASET", 2: "主視覺圖說範例"}),
        ("LG 表格", {0: "結果表格", 1: "05 / RESULT"}),
        ("LG 比較", {0: "方法比較", 1: "04 / CLUSTERING"}),
        ("LG 氛圍", {0: "全幅氛圍頁標題範例"}),
        ("LG 結語", {0: "CONCLUSION", 1: "Thank You", 2: "團隊名單範例"}),
    ]
    for name, texts in plan:
        slide = prs.slides.add_slide(layouts[name])
        _fill_placeholders(slide, texts)
        add_bg_movie(slide, prs)

        if name == "LG 統計":
            # 範例 KPI 卡兩張
            add_glass_card(slide.shapes, 96, 300, 470, 270, t)
            add_text(slide.shapes, 128, 340, 400, 90, "100,000", 40, t["accent1"], bold=True, mono=True, tokens=t)
            add_text(slide.shapes, 128, 460, 400, 50, "KPI 標籤範例", 16, t["textDim"], tokens=t)
            add_glass_card(slide.shapes, 590, 300, 470, 270, t)
        if name == "LG 流程":
            for i in range(5):
                add_glass_card(slide.shapes, 96 + i * 356, 300, 320, 480, t)
            add_glass_card(slide.shapes, 96, 860, 1728, 110, t)
            add_accent_bar(slide.shapes, 120, 884, 8, 62, t["accent1"])
        if name == "LG 比較":
            add_glass_card(slide.shapes, 96, 800, 1728, 140, t)
            add_accent_bar(slide.shapes, 120, 824, 8, 62, t["accent1"])


def add_calibration_slide(prs, layouts, tokens) -> None:
    """--calibration：烘圖卡 vs 原生卡並排。"""
    slide = prs.slides.add_slide(layouts["LG 內容"])
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    baked = ROOT / "assets" / "calibration" / "card.png"
    slide.shapes.add_picture(str(baked), 0, 0, prs.slide_width, prs.slide_height)
    add_glass_card(slide.shapes, 1150, 360, 560, 360, tokens)
    add_text(slide.shapes, 1182, 420, 480, 90, "1,728 萬次", 40, tokens["accent1"], bold=True, mono=True, tokens=tokens)
    add_text(slide.shapes, 1182, 540, 480, 50, "原生形狀卡（比對右側烘圖）", 16, tokens["textDim"], tokens=tokens)
```

- [ ] **Step 4: 寫 build_pptx.py（CLI）**

```python
"""組裝 Liquid Glass 深色 .pptx 模板。
用法：python3 build_pptx.py [-o dist/liquid-glass-dark.pptx] [--calibration]"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pptx import Presentation  # noqa: E402

from builder import load_tokens  # noqa: E402
from builder.components import add_component_slides  # noqa: E402
from builder.content import add_calibration_slide, add_example_slides  # noqa: E402
from builder.layouts import build_layouts  # noqa: E402
from builder.theme import write_theme  # noqa: E402


def build(out_path, calibration: bool = False) -> None:
    tokens = load_tokens()
    prs = Presentation(HERE / "skeleton.pptx")
    write_theme(prs, tokens)
    layouts = build_layouts(prs, tokens)
    add_example_slides(prs, layouts, tokens)
    add_component_slides(prs, layouts, tokens)
    if calibration:
        add_calibration_slide(prs, layouts, tokens)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)
    print(f"built: {out_path}（{out_path.stat().st_size / 1048576:.1f} MB）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", default=str(HERE / "dist" / "liquid-glass-dark.pptx"))
    ap.add_argument("--calibration", action="store_true")
    args = ap.parse_args()
    build(args.o, calibration=args.calibration)
```

- [ ] **Step 5: 跑到綠 + 全套回歸**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests -v
```
Expected: 全 PASS。已知坑：`add_movie` 需要 ffprobe 不在 PATH 時退化——本機 ffmpeg 已裝於 /opt/homebrew/bin，若 add_movie 拋 speaklater 類錯誤改傳 `mime_type='video/mp4'`（已傳）。

- [ ] **Step 6: 實體產出一份**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && python3 build_pptx.py --calibration
```
Expected: `dist/liquid-glass-dark.pptx` 產生，回報 MB 數。

- [ ] **Step 7: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/builder presentation/build_pptx.py presentation/tests/test_examples.py && git commit -m "feat(presentation): 範例頁與動態背景嵌入，build_pptx CLI 成形"
```

---

### Task 11: LibreOffice 煙霧測試 + README + 定版

**Files:**
- Create: `presentation/tests/test_smoke.py`
- Create: `presentation/README.md`

**Interfaces:**
- Consumes: Task 10 的 `build_pptx.build`。

- [ ] **Step 1: 寫 tests/test_smoke.py**

```python
"""開檔煙霧測試：python-pptx 讀回 + （有裝時）LibreOffice headless 轉檔不炸。"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def dist(tmp_path_factory):
    import build_pptx

    out = tmp_path_factory.mktemp("smoke") / "t.pptx"
    build_pptx.build(out)
    return out


def test_pptx_reads_back(dist):
    prs = Presentation(dist)
    assert len(list(prs.slides)) >= 11  # 9 範例 + 2 元件庫


SOFFICE = shutil.which("soffice") or (
    "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if Path("/Applications/LibreOffice.app").exists() else None)


@pytest.mark.skipif(SOFFICE is None, reason="LibreOffice 未安裝")
def test_libreoffice_converts(dist, tmp_path):
    r = subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(tmp_path), str(dist)],
        capture_output=True, timeout=180)
    assert r.returncode == 0, r.stderr.decode()[:500]
    assert list(tmp_path.glob("*.pdf")), "LibreOffice 未產出 PDF"
```

- [ ] **Step 2: 跑全套測試**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && python3 -m pytest presentation/tests -v
```
Expected: 全 PASS（LibreOffice 未裝時 smoke 顯示 SKIPPED，屬正常）。

- [ ] **Step 3: 寫 presentation/README.md**

```markdown
# Liquid Glass Presentation Template

用 Liquid Glass Kit 產出的深色 PowerPoint 模板（16:9）。產物：`dist/liquid-glass-dark.pptx`。

## 管線

    ./media.sh            # 背景影片 -> loop mp4 / gif / 靜態首幀（需 ffmpeg）
    node bake.mjs         # 母版 HTML -> @2x 底圖（需 npm install 過）
    python3 build_pptx.py # 組裝 .pptx（--calibration 附校準頁）
    python3 -m pytest tests -v

## 使用約定

- 要動態波浪背景：**複製範例頁**改內容（動態層是頁上最底層的影片物件）。
- 快速新頁（靜態背景）：從版面配置新增，九個 LG 版型任選。
- 新元件：從簡報尾端的元件庫頁複製 KPI 卡、note bar、chip、編號卡、表格。
- 字型：需安裝 Inter、Noto Sans TC、Geist Mono；對外交付前用 PowerPoint「內嵌字型」另存。
- 投影可讀性：內文不小於 24pt，發光僅限 KPI 數字。

## 換主題

改 `tokens.json` + `masters/theme-dark.css`（測試把關同步）→ 依序重跑三段管線。

## 已知限制

- 影片 autoplay/loop 由 timing XML 寫入，舊版 PowerPoint 行為可能不同；GIF 版（assets/media/wave-loop.gif）為備援。
- 母版 HTML 的玻璃是真 backdrop-filter；PPT 原生卡為近似配方，以 `--calibration` 頁比對。
```

- [ ] **Step 4: 定版 build 並讓 owner 驗收**

```bash
cd /Users/charles88/Desktop/UI-ToolBox/presentation && python3 build_pptx.py --calibration && open dist/liquid-glass-dark.pptx
```
Expected: PowerPoint 開啟無修復警告。Owner 依 spec §6 驗收清單逐項檢查（放映動態、改字搬卡、從 layout 新增、元件複製、GIF vs mp4 比較）。

- [ ] **Step 5: Commit**

```bash
cd /Users/charles88/Desktop/UI-ToolBox && git add presentation/tests/test_smoke.py presentation/README.md && git commit -m "feat(presentation): 煙霧測試與 README，模板管線完工"
```

---

## Self-Review 紀錄

- Spec 覆蓋：§3 結構（T1/T2/T3/T4/T7/T10/T11）、§4.1 media（T2）、§4.2 bake 三類產物（T4/T5/T6）、§4.3 theme/layout/玻璃卡/元件庫/範例/校準旗標（T7/T8/T9/T10）、§5 動線（README，T11）、§6 驗收（T11 Step 4 + smoke）、§7 風險（LibreOffice smoke、GIF 備援、校準頁）。無缺口。
- Placeholder 掃描：無 TBD/TODO；「佔位」字樣皆為模板的實際 placeholder 文案，非計畫缺漏。
- 型別/命名一致性：`PX`、`load_tokens`、`write_theme(prs, tokens)`、`build_layouts(prs, tokens) -> dict[name, layout]`、`add_glass_card(shapes, x, y, w, h, tokens)`、`add_text(..., tokens=None)`、`add_component_slides(prs, layouts, tokens)`、`add_example_slides(prs, layouts, tokens)`、`add_bg_movie(slide, prs)`、`build(out_path, calibration)` 於各 task 間簽名一致。
- API 查證（對本機 python-pptx 1.0.2 原始碼，2026-07-14）：`XmlPart.__init__(partname, content_type, package, element)` 參數順序正確；`get_or_add_image_part` 回傳 `(image_part, rId)`；`add_movie(..., poster_frame_image, mime_type)` 正確；media part 以 sha1 去重（9 頁同 mp4 只存一份）；`iter_parts/related_part/drop_rel/part_related_by/relate_to` 皆存在。
- 修正紀錄：`add_glass_card` 移除 `shadow.inherit = False`（避免雙 effectLst schema 違規）；`_fill_srgb` 改走 spPr XML 路徑（不碰 ColorFormat 私有屬性）；`test_component_slides_exist` 改單一斷言；hairline 斷言改精確比對；bake.mjs 移除兩處冗餘 addStyleTag。
- 已驗事項：`add_slide` 會把 layout placeholder 的「佔位文字」實體複製進 slide——Task 10 的 `plan` 文字對照表已覆蓋每個版型的全部 placeholder idx，不會殘留佔位字；日後改 `layouts_spec` 增 placeholder 時，`content.py` 的對照表必須同步補 key。
```
