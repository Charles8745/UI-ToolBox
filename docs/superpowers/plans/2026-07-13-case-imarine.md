# iMarine 實戰案例收錄（Patterns 層）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 iMarine-FrontEnd 的四組實戰 pattern 蒸餾成 UI-ToolBox 的 patterns 層文件（case-imarine.md + 6 張截圖 + llms.txt + AGENTS.md + README/CLAUDE.md 導引），讓人與 AI 用這個 Kit 時有可模仿的參照。

**Architecture:** 純文件工程，不動 Kit 本體與展示站。截圖用 Playwright headless 對 iMarine 自起的獨立 dev server 現拍（anatomy 標註以注入 HTML 疊層完成），token 值一律從 iMarine `src/ui/tokens.css` 實碼逐字抽取。llms.txt / AGENTS.md 只指路，內容單一真相在 README 與案例文件。

**Tech Stack:** Markdown、Playwright（借 iMarine 的 devDependency，經 `createRequire` 載入）、cwebp（`/opt/anaconda3/bin/cwebp`）。

**Spec:** `docs/superpowers/specs/2026-07-13-case-imarine-design.md`（九節，驗收標準見 spec §7）。

## Global Constraints

- 工作 repo：`~/Desktop/UI-ToolBox`。iMarine repo（`~/Desktop/2026航港大數據創意應用競賽/iMarine-FrontEnd`）**全程唯讀**（起 dev server 拍圖不算改動；結束時 `git -C <iMarine> status` 必須 clean）。
- 零回歸：`liquid-glass.css`、`liquid-glass.js`、`index.html`、`site.src.html`、`build_site.py`、既有 `docs/*.webp` 零 diff。
- token 保真：文件內每個 CSS 值與 iMarine `src/ui/tokens.css` 實碼逐字一致；比對基準 iMarine commit `89b8d4a`。
- 篇幅紀律：case-imarine.md §5 補充規格 ≤ 50 行；AGENTS.md ≤ 50 行。
- 截圖：webp、單張 < 300KB、畫面不得入鏡 key/後端位址等敏感資訊。
- 文字：繁體中文 + 英文術語混用；新檔案不用 emoji。
- Commit：author charles，訊息不加任何 Claude/Anthropic 署名（無 `Co-Authored-By`）；訊息風格比照本 repo 既有（中文、精簡）。
- 臨時檔（截圖腳本、PNG 中間檔）一律放 scratchpad，不進任何 repo。
- 截圖管線自起的 dev server 用 port **5330**（`--strictPort`），跑畢必須 kill 並以 `lsof -ti tcp:5330` 確認清空；不得動使用者既有服務（:5173/:5174/:8000/:8100/:8545）與 iMarine `.env`。

---

### Task 1: 截圖管線 — 6 張 webp 產入 `docs/case-imarine/`

**Files:**
- Create: `docs/case-imarine/hero-cover.webp`、`hero-overview.webp`、`rhythm-anatomy.webp`、`hue-anatomy.webp`、`carbon-doc.webp`、`twin-spatial.webp`
- Create（scratchpad，不進版控）: `<scratchpad>/shoot-case-imarine.mjs`

**Interfaces:**
- Produces: 6 個 webp 檔名如上，供 Task 2（文件引用）與 Task 5（README 引用 `hero-overview.webp`）使用。檔名即契約，後續 task 直接以此路徑寫 markdown 圖連結。

**背景知識（iMarine 實況，已核實）：**
- 路由：hash `#/<id>`，id ∈ hero/carbon/policy/twin/dispatch/epidemic/alert/agent/settings。hero 兩段式：載入即 cover 態，按 `Enter` 切總覽（ov 態）。
- 統一頁首由 `screenHeader()` 渲染：`.active header .eyebrow`（圓點+小標）與 `.trow`（h1+`.lg-chip` 徽章+`.src` 資料源 chip）。KPI 列 class `.stats4`，主視覺+右欄 class `.cols`（`1.55fr 1fr`）。左側導覽 `#rail`，active 鈕 `.rbtn.on`，色相經 CSS 變數 `--mc` 注入。
- 並非每頁都同時有 `.stats4` + `.cols`（dispatch 用自己的 `.hero`+`.dcols` 版面），所以 anatomy 頁要**先探測再選頁**（見 Step 1 腳本）。
- twin 是 WebGL：headless 需 SwiftShader（launch args 加 `--use-angle=swiftshader`，**勿加** `--disable-gpu`）。
- carbon/policy 後端未起會有 `ERR_CONNECTION_REFUSED` console（既有事實），頁面走 mock fallback 照渲染，不影響截圖。

- [ ] **Step 1: 寫截圖腳本到 scratchpad**

```js
// <scratchpad>/shoot-case-imarine.mjs — 一次性截圖管線，不進版控
import { createRequire } from 'module';
import { spawn, execSync } from 'child_process';
import { mkdirSync, statSync } from 'fs';

const IMARINE = '~/Desktop/2026航港大數據創意應用競賽/iMarine-FrontEnd';
const OUT_PNG = process.argv[2]; // scratchpad 下的中間檔目錄
const require = createRequire(IMARINE + '/package.json');
const { chromium } = require('playwright');

mkdirSync(OUT_PNG, { recursive: true });

// 1) 起獨立 dev server :5330（strictPort，直跑 vite bin，不經 npx）
const server = spawn('node', ['node_modules/vite/bin/vite.js', '--port', '5330', '--strictPort'],
  { cwd: IMARINE, stdio: 'ignore' });
const ready = async () => {
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch('http://localhost:5330/'); if (r.ok) return; } catch {}
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error('dev server :5330 起不來');
};

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// 標註疊層：對 targets 逐一畫框+標籤（綠框、深底標籤、mono 字）
const ANNOTATE = (targets) => {
  document.querySelectorAll('.__anno').forEach(n => n.remove());
  for (const t of targets) {
    const el = document.querySelector(t.sel);
    if (!el) continue;
    const r = el.getBoundingClientRect();
    const box = document.createElement('div');
    box.className = '__anno';
    box.style.cssText = `position:fixed;left:${r.left - 4}px;top:${r.top - 4}px;` +
      `width:${r.width + 8}px;height:${r.height + 8}px;border:2px solid #35E0A6;` +
      `border-radius:10px;z-index:99999;pointer-events:none;box-shadow:0 0 0 2000px rgba(0,0,0,0);`;
    const tag = document.createElement('div');
    tag.textContent = t.label;
    tag.style.cssText = `position:absolute;left:0;top:-26px;background:rgba(7,11,17,.92);` +
      `color:#35E0A6;font:600 12px "Geist Mono",monospace;padding:3px 10px;border-radius:6px;` +
      `border:1px solid rgba(53,224,166,.45);white-space:nowrap;`;
    if (t.tagBottom) { tag.style.top = 'auto'; tag.style.bottom = '-26px'; }
    box.appendChild(tag);
    document.body.appendChild(box);
  }
};

try {
  await ready();
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 2 });
  const goto = async (hash, wait) => { await page.goto('http://localhost:5330/' + hash); await sleep(wait); };
  const shot = (name) => page.screenshot({ path: `${OUT_PNG}/${name}.png` });

  // (1) hero 封面（cover 態，波浪影片 + 輕 scrim）
  await goto('#/hero', 3500); await shot('hero-cover');
  // (2) hero 總覽（Enter 切 ov 態）
  await page.keyboard.press('Enter'); await sleep(2500); await shot('hero-overview');

  // (3) 頁面節奏 anatomy：探測第一個同時有 .eyebrow/.stats4/.cols 的頁
  const cand = ['dispatch', 'alert', 'epidemic', 'carbon', 'policy'];
  let rhythmPage = null;
  for (const id of cand) {
    await goto('#/' + id, 3000);
    const ok = await page.evaluate(() =>
      !!document.querySelector('.active header .eyebrow') &&
      !!document.querySelector('.active .stats4') &&
      !!document.querySelector('.active .cols'));
    if (ok) { rhythmPage = id; break; }
  }
  if (!rhythmPage) throw new Error('無頁面同時具備 .eyebrow/.stats4/.cols，需人工回報');
  console.log('rhythm anatomy 用頁：', rhythmPage);
  await page.evaluate(ANNOTATE, [
    { sel: '.active header .eyebrow', label: '1 EYEBROW 標頭（模組色圓點 + mono 小標）' },
    { sel: '.active header .trow', label: '2 標題列（h1 + 技術徽章 + 資料源 chip）' },
    { sel: '.active .stats4', label: '3 KPI 統計列（lg-stat ×4）' },
    { sel: '.active .cols > *:first-child', label: '4 主視覺 ~62%', tagBottom: true },
    { sel: '.active .cols > *:last-child', label: '5 右欄卡', tagBottom: true },
  ]);
  await sleep(300); await shot('rhythm-anatomy');

  // (4) 色相三合法位置 anatomy：epidemic（玫紅 #F0648C，rail active + eyebrow 圓點 + 徽章同框）
  await goto('#/epidemic', 3000);
  await page.evaluate(ANNOTATE, [
    { sel: '#rail .rbtn.on', label: '1 rail active' },
    { sel: '.active header .eyebrow .dot', label: '2 eyebrow 圓點' },
    { sel: '.active header .trow .lg-chip', label: '3 徽章' },
  ]);
  await sleep(300); await shot('hue-anatomy');

  // (5) carbon：doc 態 scrim 壓暗對照（mock fallback 渲染即可）
  await goto('#/carbon', 3500); await shot('carbon-doc');
  // (6) twin：空間態背景亮對照（WebGL，SwiftShader）
  await goto('#/twin', 5000); await shot('twin-spatial');

  await browser.close();
} finally {
  server.kill();
  await sleep(1000);
  try { execSync('lsof -ti tcp:5330'); console.error('WARN: :5330 未清空'); }
  catch { console.log(':5330 已清空'); }
}
```

- [ ] **Step 2: 跑腳本產 PNG**

Run: `node "<scratchpad>/shoot-case-imarine.mjs" "<scratchpad>/case-shots"`
Expected: stdout 印出 `rhythm anatomy 用頁： <id>`（大概率 `alert` 或 `epidemic`；若是 dispatch 以外的頁，記進 task 報告——文件 §2 圖說要寫實際頁名）與 `:5330 已清空`；`<scratchpad>/case-shots/` 出現 6 張 PNG。

- [ ] **Step 3: 人眼（讀圖）檢查 6 張 PNG**

逐張確認：版面完整非全黑、標註框對準部位、標籤文字可讀、無 key/後端位址入鏡（settings 頁不在拍攝清單內，本來就不會入鏡）。hero-cover 需可見背景影片畫面；twin-spatial 需可見點雲/場景（非黑屏——SwiftShader 失效時會黑屏，若黑屏改查 launch args）。

- [ ] **Step 4: 轉 webp 並落位**

```bash
mkdir -p ~/Desktop/UI-ToolBox/docs/case-imarine
cd "<scratchpad>/case-shots"
for f in hero-cover hero-overview rhythm-anatomy hue-anatomy carbon-doc twin-spatial; do
  /opt/anaconda3/bin/cwebp -q 82 -resize 1600 0 "$f.png" -o "~/Desktop/UI-ToolBox/docs/case-imarine/$f.webp"
done
ls -la ~/Desktop/UI-ToolBox/docs/case-imarine/
```

Expected: 6 個 webp，每張 < 300KB（`-q 82 -resize 1600 0` 對照既有 docs/*.webp 75-95KB 水準，若超標降 `-q` 至 75 重轉）。

- [ ] **Step 5: 確認 iMarine 零改動 + commit**

```bash
git -C "~/Desktop/2026航港大數據創意應用競賽/iMarine-FrontEnd" status --short   # 必須空
cd ~/Desktop/UI-ToolBox
git add docs/case-imarine/
git commit -m "docs(case): iMarine 案例截圖 6 張（2 張 anatomy 標註）"
```

---

### Task 2: `docs/case-imarine.md` 開場 + §1–§4

**Files:**
- Create: `docs/case-imarine.md`

**Interfaces:**
- Consumes: Task 1 的 6 個 webp 檔名。
- Produces: 文件骨架與 §1-§4；Task 3 在檔尾續寫 §5/§6，不改本 task 內容。

**寫法通則（每個 pattern 節固定結構，spec §4）**：一句 why → When to use / NOT → 規則（Do/Don't 成對）→ 可複製代碼 → 截圖。截圖只是佐證，拿掉圖文件仍自足。

- [ ] **Step 1: 寫開場 + §1-§4**

以下為必須包含的關鍵內容（措辭可潤飾、代碼塊逐字照抄不得改值）：

**開場（~15 行）**：iMarine = 2026 航港大數據創意應用競賽前端，9 screens、深色 Liquid Glass、Vite + vanilla TS shell，全部用本 Kit 的 class 拼、零自訂玻璃 CSS。本文四個 pattern 借 Material Design 語彙：§1/§3/§4 為 foundations 實戰、§2 為 canonical layout（supporting pane 變體）。文末 §5 有可直接貼給 AI 的補充規格。放 `![iMarine 戰情總覽](case-imarine/hero-overview.webp)`。

**§1 深色主題 tokens 系統（foundations）**
- Why：Kit 展示站語境偏亮色；深色下的文字梯度、髮絲線、緩動需要一套已驗證的值。
- When to use：暗場景儀表板、監控台、簡報 demo。When NOT：內容閱讀型長文頁。
- 規則（Do/Don't 成對）：
  - Do 文字梯度只用 ink 四階；Don't 用任意灰值。
  - Do 分隔線/邊框一律 `--hair`；Don't 用實色灰線。
  - Do 動畫緩動一律 `--ease`；Don't 混用多條 easing 曲線。
  - Do 數據、代碼、eyebrow 小標用 `--mono`；Don't 全頁 monospace。
- 可複製代碼（逐字抄自 iMarine `src/ui/tokens.css`，commit `89b8d4a`）：

```css
:root{
  --lg-accent:#35E0A6;
  --bg:#070b11;
  --gold:#E9BC63; --cyan:#38BDF8; --amber:#F5A54A; --rose:#F0648C; --flame:#FF7A59;
  --ink-90:rgba(255,255,255,.92); --ink-60:rgba(255,255,255,.62);
  --ink-50:rgba(255,255,255,.5); --ink-40:rgba(255,255,255,.4);
  --hair:rgba(255,255,255,.1);
  --ease:cubic-bezier(.22,1,.36,1);
  --mono:"Geist Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
body{
  background:var(--bg);color:var(--ink-90);
  font-family:"Inter","Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;
}
```

- Kit 銜接：`document.documentElement.setAttribute('data-lg-theme', 'dark')`（或 `<html data-lg-theme="dark">`），Kit 元件即切深色皮。

**§2 儀表板頁面節奏（canonical layout：supporting pane 變體）**
- Why：多頁產品需要每頁一致的縱向節奏，使用者換頁不用重新學版面。
- 公式五步：eyebrow 標頭 → 標題列（h1 + 技術徽章 + 資料源 chip）→ KPI/狀態列（頁面特化）→ 主視覺（~62%）+ 右欄卡 → stagger 進場。其中 eyebrow+標題列（screenHeader）與 stagger 是七頁真·共用；KPI/狀態列與 body 二欄由各頁依內容特化（見下方誠實註記）。
- 規則：
  - Do 進場 stagger 用 `.anim` + `style="--d:.08s"` 遞增（頁首固定 `--d:0s` 最先進場）；Don't 全頁同時進場。
  - Do KPI 卡守「玻璃容器 + 實心內容」鐵則（數字、sparkline 不透明）；Don't 在內容上再蓋玻璃。
  - Do 小型/大量重複元件用 `lg-static`；Don't 每列都掛折射。
  - Do 資料源如實顯示（live 綠 chip / mock 灰 chip）；Don't 假裝 live。
- 可複製代碼（頁面 HTML 骨架）：`<header>` 區塊為 iMarine `screenHeader()` 的**實際輸出**（七頁共用，逐字忠實）；`.stats4`/`.cols`/`.stack` 為 tokens.css 提供的**版面基元**（值真實、可直接套用）：

```html
<header class="anim" style="--d:0s">
  <div class="eyebrow"><span class="dot" style="--mc:#F5A54A"></span><span class="lbl">航港局視角 · MODULE 04</span></div>
  <div class="trow">
    <h1>短時微氣候 · 即時派工建議</h1>
    <span class="lg-chip">ConvLSTM</span><span class="lg-chip">CWA 開放資料</span>
    <span class="src"><i></i>MOCK 資料</span>
    <span class="spacer"></span>
  </div>
</header>

<div class="stats4 anim" style="--d:.08s">
  <div class="lg lg-stat" data-lg>
    <span class="lg-stat__label">平均風速</span>
    <span class="lg-stat__value" data-lg-value="7.2" data-lg-decimals="1" data-lg-suffix=" m/s">0</span>
    <span class="lg-stat__delta">+0.8 vs 前 1h</span>
    <svg class="lg-stat__spark" data-lg-spark="5,6,6.5,7,7.2"></svg>
  </div>
  <!-- 同構 lg-stat 共 4 張 -->
</div>

<div class="cols">
  <div class="lg lg-card anim" data-lg style="--d:.14s">
    <!-- 主視覺：圖表 / 地圖 / 時間軸（實心內容層） -->
  </div>
  <div class="stack">
    <div class="lg lg-card anim" data-lg style="--d:.20s"><!-- 右欄卡 1 --></div>
    <div class="lg lg-card anim" data-lg style="--d:.26s"><!-- 右欄卡 2 --></div>
  </div>
</div>
```

- 配套格線 CSS（逐字抄自 tokens.css）：

```css
.stats4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}
.cols{display:grid;grid-template-columns:1.55fr 1fr;gap:16px;align-items:start;}
.stack{display:flex;flex-direction:column;gap:14px;}
```

（`1.55fr/1fr` 即主視覺 ~62%——supporting pane 的比例。）
- **誠實註記（撰稿者務必寫進文件，Task 1 實作查證）**：`.stats4`/`.cols` 是 tokens.css 的版面基元、值真實可直接用，但目前各功能頁多半**特化自己的 body 版面**——carbon 用 4-up `.stats` KPI grid、dispatch 用 62:38 `.dcols` supporting pane、policy 用 `.pcols`。七頁真正共用的是「頁首 `screenHeader()` + `.anim` stagger + supporting pane 的**概念**」，不是逐字同名的 body class。文件請以此框架敘述（把 `.stats4`/`.cols` 定位為「設計層提供、頁面可套用或特化的基元」），**勿宣稱每頁都用 `.stats4`/`.cols`**。
- Anatomy 圖：`![頁面節奏 anatomy（dispatch 頁）](case-imarine/rhythm-anatomy.webp)`，圖說寫明實拍頁 = **dispatch**；並註明此頁第 3 區塊（`.hero`）是「狀態彙總列（天候/結論時間軸/模型倒數環）」而非四張同構 KPI 卡（4-up KPI 的實例在 carbon 的 `.stats`），第 4/5 區塊是 `.dcols` 的 62:38 二欄。

**§3 模組輔助色相系統（foundations：多模組識別色紀律）**
- Why：多模組產品需要識別色，但玻璃介面大面積上彩會毀掉材質感。
- 核心機制：色相只經 CSS 變數 `--mc` 注入，元件樣式寫一次、換模組只換一個變數，零樣式分支（逐字抄自實碼）：

```css
.eyebrow .dot{background:var(--mc,#35E0A6);box-shadow:0 0 10px var(--mc,#35E0A6);}
.rbtn.on{background:color-mix(in srgb,var(--mc,#35E0A6) 20%,transparent);}
```

用法：`<span class="dot" style="--mc:#F5A54A"></span>`。
- 規則：
  - Do 色相只出現在三個位置：導覽 rail active、eyebrow 圓點、徽章；Don't 拿色相當卡片底色或大面積填色。
  - Do 主行動色（按鈕、live chip、正向數據）永遠 `--lg-accent`；Don't 讓模組色搶走行動色的語意。
- 七色相表：

| 模組 | 色相 |
| --- | --- |
| carbon 金 | `#E9BC63` |
| policy 青 | `#38BDF8` |
| twin 藍 | `#7FB4FF` |
| dispatch 琥珀 | `#F5A54A` |
| epidemic 玫紅 | `#F0648C` |
| alert 橘紅 | `#FF7A59` |
| agent 紫 | `#B48CFF` |

- Anatomy 圖：`![色相三合法位置](case-imarine/hue-anatomy.webp)`。

**§4 背景層與 scrim 兩態（foundations：玻璃的舞台）**
- Why：Kit 鐵則「頁面必須有多彩背景」的實戰放大——背景怎麼給、怎麼壓才不搶內容。
- 分層結構（z-index 由下而上）：`#harbor` 點雲 canvas → `.glowfx` 光暈 → `#veil` 暗罩 → `#backdrop` 影片 → `#backdrop-scrim` → 內容層。全站共用單一 `<video>`，換頁只換 `src`。
- 兩態：空間型頁（hero/twin）背景亮、文件型頁（表格/長文）scrim 壓暗，由 `body[data-mode]` 驅動、純 CSS 切態。
- 規則：
  - Do 影片退為氛圍：`opacity:.8` + `filter:brightness(.75)`；Don't 讓背景與內容搶對比。
  - Do scrim 用同色系（`rgba(7,11,17,x)`）漸層；Don't 用黑色純色蓋。
  - Do reduced-motion 時換 poster 靜態幀；Don't 強播影片。
- 可複製代碼（逐字抄自 tokens.css）：

```css
#backdrop{position:fixed;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;z-index:3;pointer-events:none;display:none;opacity:.8;filter:brightness(.75);}
body[data-bg="on"] #backdrop{display:block;}
#backdrop-scrim{position:fixed;inset:0;z-index:4;pointer-events:none;opacity:0;transition:opacity .3s var(--ease);
  background:linear-gradient(180deg,rgba(7,11,17,.5),rgba(7,11,17,.15) 45%,rgba(7,11,17,.62));}
body[data-bg="on"] #backdrop-scrim{opacity:1;}
body[data-bg="on"][data-mode="cover"] #backdrop-scrim{background:linear-gradient(180deg,rgba(7,11,17,.5),rgba(7,11,17,.15) 45%,rgba(7,11,17,.62));}
body[data-bg="on"][data-mode="ov"] #backdrop-scrim{background:linear-gradient(180deg,rgba(7,11,17,.72),rgba(7,11,17,.6) 45%,rgba(7,11,17,.8));}
body[data-bg="on"][data-mode="doc"] #backdrop-scrim{background:linear-gradient(180deg,rgba(7,11,17,.86),rgba(7,11,17,.8) 50%,rgba(7,11,17,.9));}
```

- 對照圖三張：`hero-cover.webp`（影片背景+輕 scrim）、`twin-spatial.webp`（空間態亮）、`carbon-doc.webp`（doc 態壓暗）。

- [ ] **Step 2: 驗證代碼塊保真**

```bash
cd ~/Desktop/UI-ToolBox
IM="~/Desktop/2026航港大數據創意應用競賽/iMarine-FrontEnd/src/ui/tokens.css"
for v in '#35E0A6' '#070b11' '#E9BC63' '#38BDF8' '#F5A54A' '#F0648C' '#FF7A59' \
         'rgba(255,255,255,.92)' 'rgba(255,255,255,.62)' 'rgba(255,255,255,.1)' \
         'cubic-bezier(.22,1,.36,1)' 'brightness(.75)' '1.55fr 1fr' \
         'rgba(7,11,17,.86)' 'rgba(7,11,17,.72)'; do
  grep -qF "$v" docs/case-imarine.md && grep -qF "$v" "$IM" && echo "OK  $v" || echo "FAIL $v"
done
```

Expected: 全部 `OK`（twin `#7FB4FF` 與 agent `#B48CFF` 不在 tokens.css——它們在 registry/settings 定義，只驗文件端存在即可：`grep -c '7FB4FF\|B48CFF' docs/case-imarine.md` ≥ 2）。

- [ ] **Step 3: Commit**

```bash
git add docs/case-imarine.md
git commit -m "docs(case): iMarine 案例文件 開場+§1-§4（tokens/頁面節奏/色相/背景層）"
```

---

### Task 3: `docs/case-imarine.md` §5 補充規格 + §6 變更紀錄

**Files:**
- Modify: `docs/case-imarine.md`（檔尾追加）

**Interfaces:**
- Consumes: Task 2 的 §1-§4（§5 是其濃縮，不得引入 §1-§4 沒有的新值）。
- Produces: §5 的 code block 全文（Task 6 AI 盲測直接取用）；§6 記 iMarine commit `89b8d4a`。

- [ ] **Step 1: 追加 §5（code block 全文如下，≤50 行，實測 38 行）**

````markdown
## §5 貼給 AI 的補充規格

以下純文字接在 README「AI 使用規格」主規格之後貼給 AI 使用；與主規格衝突時以主規格為準。

```text
# Liquid Glass Kit — 深色儀表板補充規格（接在主規格之後）
來源：iMarine 實戰案例（docs/case-imarine.md）。

## 深色 tokens（:root 覆寫 + <html data-lg-theme="dark">）
:root{ --lg-accent:#35E0A6; --bg:#070b11;
  --gold:#E9BC63; --cyan:#38BDF8; --amber:#F5A54A; --rose:#F0648C; --flame:#FF7A59;
  --ink-90:rgba(255,255,255,.92); --ink-60:rgba(255,255,255,.62);
  --ink-50:rgba(255,255,255,.5); --ink-40:rgba(255,255,255,.4);
  --hair:rgba(255,255,255,.1); --ease:cubic-bezier(.22,1,.36,1); }
body{background:var(--bg);color:var(--ink-90);
  font-family:"Inter","Noto Sans TC",system-ui,sans-serif;}
規則：文字只用 ink 四階；分隔線只用 --hair；緩動只用 --ease；數據與小標用 monospace。

## 頁面節奏（由上而下，每頁一致）
1 eyebrow（模組色圓點 + mono 小標）→ 2 標題列（h1 + lg-chip 技術徽章 + 資料源 chip）
→ 3 KPI 統計列（lg-stat ×4）→ 4 主視覺(~62%) + 右欄卡（grid 1.55fr/1fr）
→ 5 stagger 進場（.anim + style="--d:.08s" 遞增，頁首 --d:0s）。
儀表鐵則：玻璃只做容器，數字/圖表/sparkline 為實心內容層。
資料源 chip 如實顯示：live 綠 / mock 灰。

## 模組識別色（多模組產品）
每模組一色相，只准出現在三個位置：導覽 active 態、eyebrow 圓點、徽章。
Don't：拿色相當卡片底色或大面積填色。主行動色永遠 --lg-accent。
機制：元件樣式吃 var(--mc)，換模組只換 style="--mc:#..."，零樣式分支。
範例盤：金 #E9BC63 青 #38BDF8 藍 #7FB4FF 琥珀 #F5A54A 玫紅 #F0648C 橘紅 #FF7A59 紫 #B48CFF

## 背景與 scrim（玻璃的舞台）
頁面必須有多彩/動態背景；內容層之下依序：背景（圖/影片/canvas）→ scrim 漸層 → 內容。
影片退為氛圍：opacity:.8 + filter:brightness(.75)。
scrim 同色系漸層 rgba(7,11,17,x)，依頁型三態：封面輕(.5) / 空間頁略暗(.72) / 文件頁重(.86)。
reduced-motion：影片換 poster 靜態幀。
```
````

- [ ] **Step 2: 追加 §6 變更紀錄**

```markdown
## §6 變更紀錄

| 日期 | iMarine commit | 摘要 |
| --- | --- | --- |
| 2026-07-13 | `89b8d4a` | 初版：自 tokens.css 抽取四組 pattern + 6 張截圖 |
```

- [ ] **Step 3: 驗證篇幅 + commit**

```bash
# §5 的 text code block 行數 ≤ 50（取兩個 ```text 圍欄間行數）
awk '/^```text$/{f=1;n=0;next} /^```$/{if(f){print n;f=0}} f{n++}' docs/case-imarine.md
git add docs/case-imarine.md
git commit -m "docs(case): §5 貼給 AI 的補充規格（38 行）+ §6 變更紀錄"
```

Expected: awk 輸出 ≤ 50。

---

### Task 4: `llms.txt` + `AGENTS.md`

**Files:**
- Create: `llms.txt`（repo 根）
- Create: `AGENTS.md`（repo 根）

**Interfaces:**
- Consumes: `docs/case-imarine.md`（Task 2/3 已存在，連結才有效）。
- Produces: 兩個指路檔；Task 6 驗連結有效性。

- [ ] **Step 1: 寫 `llms.txt`（llmstxt.org 規範：H1 + blockquote + H2 連結清單 + Optional）**

```markdown
# Liquid Glass Kit

> 零依賴液態玻璃 UI 工具包：18 個元件、Snell 定律即時折射、發光背景、慣性拖曳。複製 liquid-glass.css + liquid-glass.js 兩檔即可用，為 AI 協作而生。折射僅 Chromium 完整支援，其他瀏覽器自動降級磨砂。

## 核心

- [README](README.md): 人類入口；內含「AI 使用規格」全文（元件結構、鐵則、JS API，可直接貼給 AI）
- [liquid-glass.css](liquid-glass.css): 工具包樣式
- [liquid-glass.js](liquid-glass.js): 工具包引擎

## 實戰 Patterns

- [iMarine 深色儀表板案例](docs/case-imarine.md): 深色 tokens、頁面節奏（supporting pane）、模組色相紀律、背景層與 scrim；§5 有可貼給 AI 的補充規格

## Optional

- [AGENTS.md](AGENTS.md): 給使用本 Kit 的 AI agent 的精簡指引
- [CLAUDE.md](CLAUDE.md): 維護本 repo 的開發規則（建置流程、鐵律）
```

- [ ] **Step 2: 寫 `AGENTS.md`（≤50 行）**

```markdown
# Liquid Glass Kit — Agent 指引

> 給「使用本 Kit 開發介面」的 AI agent。要維護本 repo（改 Kit 本體或展示站）請改讀 CLAUDE.md。

## 這是什麼

零依賴液態玻璃 UI 工具包：liquid-glass.css + liquid-glass.js 兩檔即可用，18 個現成元件。
折射僅 Chromium 完整支援，其他瀏覽器自動降級為磨砂玻璃，版面與互動不變。

## 開始之前

- 元件規格單一真相：README 的「AI 使用規格」（含一鍵複製全文），先讀再動手。
- 深色主題 / 儀表板 / 多模組產品需求：先讀 docs/case-imarine.md
  （實戰 patterns：深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim），
  其 §5 是可直接接在主規格之後使用的補充規格。

## 鐵則（違反即錯）

1. 玻璃只用於浮在內容之上的控制層（導航、卡片、面板、對話框、dock）；內容本身不上玻璃。
2. 折射玻璃 = class="lg" + data-lg；小型或大量重複的元件改用 class="lg lg-static"。
3. 頁面必須有圖像或多彩背景，玻璃效果才看得見。
4. 不要手寫 backdrop-filter 或自製玻璃 CSS，一律用工具包的 class 與 API。
5. 動態插入的節點呼叫 LiquidGlass.attach(el)。
6. 儀表元件 = 玻璃容器 + 實心內容層：數字、走勢圖、圖表本身不透明。

## 快速起手

    <link rel="stylesheet" href="liquid-glass.css">
    <script src="liquid-glass.js"></script>
    <script>LiquidGlass.init();</script>

## 文件地圖

- README.md：人類入口 + AI 使用規格全文
- docs/case-imarine.md：深色儀表板實戰案例（patterns 層）
- llms.txt：機器可讀索引
- CLAUDE.md：維護者專用（建置流程與鐵律）
```

- [ ] **Step 3: 驗證 + commit**

```bash
cd ~/Desktop/UI-ToolBox
wc -l AGENTS.md        # ≤ 50
head -3 llms.txt       # H1 + 空行 + blockquote
git add llms.txt AGENTS.md
git commit -m "docs: llms.txt 機器可讀索引 + AGENTS.md 外部 agent 指引"
```

---

### Task 5: README「實戰案例」節 + CLAUDE.md 導引

**Files:**
- Modify: `README.md`（「用這套能做出什麼」節末，深色主題段之後、line 27 `---` 之前插入）
- Modify: `CLAUDE.md`（`## AI 規格書` 節之前插入小節）

**Interfaces:**
- Consumes: `docs/case-imarine/hero-overview.webp`（Task 1）、`docs/case-imarine.md`（Task 2/3）。

- [ ] **Step 1: README 插入（比照該區塊既有格式：粗體標題 — 說明 + 圖）**

在「**深色主題**…」段落與其圖之後、`---` 之前插入：

```markdown
**實戰案例 — 永續智能航港生態系(iMarine)** — 9 個 screen 的深色儀表板全站,從封面到六大功能頁全部用 Kit 的 class 拼出,零自訂玻璃 CSS:

![iMarine 戰情總覽](docs/case-imarine/hero-overview.webp)

> 深色 tokens、頁面節奏、模組識別色紀律、背景層與 scrim 的完整拆解,以及一份可直接貼給 AI 的「深色儀表板補充規格」,見 **[docs/case-imarine.md](docs/case-imarine.md)**。
```

（注意：README 既有文風用半形逗號 `,`，照抄此風格。）

- [ ] **Step 2: CLAUDE.md 插入（`## AI 規格書` 之前）**

```markdown
## 實戰案例(patterns 層)

深色主題、儀表板、多模組介面的需求,先讀 `docs/case-imarine.md`(iMarine 案例:深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim),再動手拼版面。其 §5 是可接在 AI 規格書之後使用的補充規格。
```

- [ ] **Step 3: 驗證 + commit**

```bash
cd ~/Desktop/UI-ToolBox
grep -n "case-imarine" README.md CLAUDE.md   # 兩檔各至少 1 hit
git add README.md CLAUDE.md
git commit -m "docs: README 實戰案例節 + CLAUDE.md patterns 層導引"
```

---

### Task 6: 全案驗收（spec §7 六條逐一實跑）

**Files:**
- Modify: `HANDOFF.md`（UI-ToolBox 本機 HANDOFF，gitignored——記本輪成果與殘留）

**Interfaces:**
- Consumes: 全部前置 task 的產出。

- [ ] **Step 1: 驗收 1 — AI 盲測**

主控（非本 task 的 implementer）dispatch 一個全新 general-purpose subagent，prompt 僅含兩段文字：README「AI 使用規格」code block 全文 + case-imarine.md §5 code block 全文，任務：「用以上規格做一個深色三模組監控儀表板的單檔 HTML（模組任選，資料用假資料）。只回傳 HTML。」

對回傳 HTML 檢查四點（`grep` + 人眼讀碼）：
1. 深底非純黑：出現 `#070b11` 或 `var(--bg)`（且非 `#000`）。
2. KPI 統計列：`lg-stat` 出現 ≥ 3 次。
3. 色相紀律：模組色相（如 `--mc`）只出現在導覽 active/eyebrow 圓點/徽章類位置，卡片底色無大面積彩色。
4. 背景 + scrim：有背景層（gradient/圖/canvas 皆可）+ 有 scrim/veil 漸層壓暗。

Expected: 4/4 命中。若有未命中：回頭修 §5 的措辭（規則句式化、加 Don't），**不加長篇幅**，重測一次並如實記錄兩次結果。

- [ ] **Step 2: 驗收 2 — token 保真**

重跑 Task 2 Step 2 的 grep 迴圈。Expected: 全 OK。

- [ ] **Step 3: 驗收 3 — llms.txt 合規 + 全連結有效**

```bash
cd ~/Desktop/UI-ToolBox
# 結構：第 1 行 H1、第 3 行 blockquote
sed -n '1p;3p' llms.txt
# 連結有效性：抽出所有相對路徑連結逐一 test -e
grep -oE '\]\(([^)#]+)' llms.txt AGENTS.md README.md CLAUDE.md docs/case-imarine.md \
 | sed 's/.*(//' | sort -u | while read f; do
   [ -e "$f" ] && echo "OK  $f" || echo "MISS $f"
 done
```

Expected: 無 `MISS`（http 外連與純錨點不在此列，人工略過）。

- [ ] **Step 4: 驗收 4+5 — 零回歸 + iMarine 零改動**

```bash
cd ~/Desktop/UI-ToolBox
git status --short            # 只剩 HANDOFF.md（gitignored 故不顯示）→ 應為空
git diff HEAD~5 --stat -- liquid-glass.css liquid-glass.js index.html site.src.html build_site.py docs/*.webp
git -C "~/Desktop/2026航港大數據創意應用競賽/iMarine-FrontEnd" status --short
lsof -ti tcp:5330 || echo "port clean"
```

Expected: 第二行 diff 為空（本輪 5 個 commit 未碰這些檔）；iMarine status 空；port clean。

- [ ] **Step 5: 驗收 6 — 篇幅紀律**

```bash
awk '/^```text$/{f=1;n=0;next} /^```$/{if(f){print "§5:",n;f=0}} f{n++}' docs/case-imarine.md
wc -l AGENTS.md
```

Expected: §5 ≤ 50、AGENTS.md ≤ 50。

- [ ] **Step 6: 更新 UI-ToolBox `HANDOFF.md`（本機檔，不 commit）**

記：本輪四件產出（案例文件/截圖/llms.txt+AGENTS.md/README+CLAUDE.md 導引）、AI 盲測結果（含如果修過 §5 的紀錄）、rhythm-anatomy 實拍頁名、殘留事項（兩 repo 漂移靠 §6 變更紀錄追蹤；日後 iMarine 換真實背景素材後可重拍 4 張非 anatomy 截圖）。

---

## Self-Review 紀錄

- **Spec coverage**：spec §3 產出物 6 項 → Task 1（截圖）、Task 2/3（案例文件）、Task 4（llms.txt/AGENTS.md）、Task 5（README/CLAUDE.md）✓；spec §7 驗收 6 條 → Task 6 六個 step 一一對應 ✓；spec §6 截圖 6 張規格 → Task 1 六連拍 + 標註 ✓。
- **Placeholder scan**：無 TBD/TODO；唯一執行期決策是 rhythm-anatomy 用頁（dispatch 版面自有 `.hero`+`.dcols`，不保證有 `.stats4`+`.cols`），已寫成探測邏輯 + 記錄要求，非 placeholder。
- **一致性**：webp 檔名在 Task 1/2/5 三處一致（hero-cover/hero-overview/rhythm-anatomy/hue-anatomy/carbon-doc/twin-spatial）；§5 值域是 §1-§4 的子集；`89b8d4a` 在 Global Constraints、Task 2、Task 3 §6 一致。
