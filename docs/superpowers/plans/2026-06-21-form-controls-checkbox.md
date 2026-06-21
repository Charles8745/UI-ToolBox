# Checkbox（`.lg-check`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增「核取方塊」元件 `.lg-check`，家族 A 第一件。

**Architecture:** 純 CSS + native `<input type="checkbox">`，**零 JS**（同 `.lg-switch`）。`<label>` 包 hidden input + 磨砂玻璃 `__box` + 文字 `__label`。box bespoke 磨砂（`backdrop-filter: blur() saturate()`，不掛 `data-lg`、不折射、不需 `attach()`）；勾用既有 `#ph-check` 圖示，實心白色；indeterminate 用 CSS `::after` 橫槓。

**Tech Stack:** `liquid-glass.css`（樣式）、`site.src.html`（展示 + AI 規格 + 程式碼庫）、`CLAUDE.md`（AI 規格書）、`python3 build_site.py`（重生 `index.html`）。**本專案無單元測試框架**——驗證 = build 通過（圖示完整性檢查 + 重生）+ grep 存在性 + Chromium 實機目視（使用者 gate）。

## Global Constraints

- 玻璃只做控制層；勾、字是實心內容層（CLAUDE.md 鐵律 5）。
- 不手寫 `backdrop-filter` 以外的自製玻璃；顏色/圓角/字型一律用既有 token，不硬編。
- 圖示引用用完整字面量 `'#ph-check'`；`check` 已在 `assets/icons.json`（不需新增圖示）。
- **不引入 `:has()`**（codebase 尚未用到）；disabled 用兄弟選擇器 `~`。
- 樣式進 `liquid-glass.css`；改完跑 `python3 build_site.py` 重生 `index.html`。
- 降級：`html.lg-fallback` 一併套磨砂；非 Chromium native checkbox 行為正常、不報錯。
- 過渡 token：`--lg-speed`=0.34s、`--lg-ease`=`cubic-bezier(0.34,1.3,0.4,1)`、`--lg-ease-out`=`cubic-bezier(0.22,0.8,0.3,1)`；勾 overshoot 用 `cubic-bezier(.34,1.56,.64,1)`。
- 既有 token 值：`--lg-radius-s`=12px、`--lg-tint`、`--lg-tint-strong`、`--lg-stroke`=0.50、`--lg-stroke-soft`=0.22、`--lg-shadow-soft`、`--lg-accent`、`--lg-text`、`--lg-font`。

---

## Task 1：Checkbox CSS + 展示 demo（使用者目視 gate）

本任務交付「可在 Chromium 看到並操作的 checkbox」。CSS 與展示 demo 綁在一起做，否則無從目視。

**Files:**
- Modify: `liquid-glass.css`（在第 8 節 `.lg-switch`（~351–401 行）之後、第 9 節 `.lg-slider`（~403 行）之前插入新節；並在 ~935 行 reduced-motion 區補一行）
- Modify: `site.src.html`（元件展示分頁 Switch tile 之後插入 Checkbox tile；底部 inline script 補 indeterminate 設定）

**Interfaces:**
- Produces（後續 Task 2 與使用者會引用的固定 class 名）：`.lg-check`、`.lg-check__box`、`.lg-check__mark`、`.lg-check__label`。HTML 結構見下方 demo。

- [ ] **Step 1：在 `liquid-glass.css` 插入 Checkbox 樣式**

在第 8 節 `.lg-switch` 區塊結束（`.lg-switch input:focus-visible + .lg-switch__track { … }` 那條，約第 401 行 `}`）之後、`/* 9. 滑桿 */` 註解之前，插入：

```css
/* ==================================================================== *
 * 8b. 核取方塊  .lg-check(純 CSS,checkbox;box 磨砂,勾為實心內容)
 * ==================================================================== */
.lg-check {
  display: inline-flex;
  align-items: center;
  gap: 11px;
  cursor: pointer;
  font: 500 14px/1 var(--lg-font);
  color: var(--lg-text);
  user-select: none;
}
.lg-check input { position: absolute; opacity: 0; width: 0; height: 0; }
.lg-check__box {
  position: relative;
  width: 22px;
  height: 22px;
  flex: none;
  border-radius: var(--lg-radius-s);
  background: var(--lg-tint);
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft);
  transition: background var(--lg-speed) var(--lg-ease-out),
              box-shadow var(--lg-speed) var(--lg-ease-out),
              scale var(--lg-speed) var(--lg-ease);
}
html.lg-fallback .lg-check__box,
.lg-check__box {
  -webkit-backdrop-filter: blur(14px) saturate(1.6);
  backdrop-filter: blur(14px) saturate(1.6);
}
.lg-check__mark {
  position: absolute;
  inset: 3px;
  width: calc(100% - 6px);
  height: calc(100% - 6px);
  color: #fff;
  fill: currentColor;
  scale: 0;
  transition: scale var(--lg-speed) cubic-bezier(.34, 1.56, .64, 1);
}
.lg-check:hover .lg-check__box {
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke);
  scale: 1.04;
}
.lg-check:active .lg-check__box { scale: 0.92; }
.lg-check input:checked + .lg-check__box,
.lg-check input:indeterminate + .lg-check__box {
  background: var(--lg-accent);
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px transparent;
}
.lg-check input:checked + .lg-check__box .lg-check__mark { scale: 1; }
.lg-check input:indeterminate + .lg-check__box .lg-check__mark { scale: 0; }
.lg-check input:indeterminate + .lg-check__box::after {
  content: "";
  position: absolute;
  left: 5px;
  right: 5px;
  top: 50%;
  height: 2px;
  border-radius: 1px;
  background: #fff;
  transform: translateY(-50%);
}
.lg-check input:focus-visible + .lg-check__box {
  outline: 2px solid var(--lg-accent);
  outline-offset: 3px;
}
.lg-check input:disabled ~ .lg-check__box,
.lg-check input:disabled ~ .lg-check__label { opacity: 0.45; }
```

> 註：spec 提到 disabled 時 `cursor:not-allowed`，但那需 `:has()`（本專案禁用）。改以 0.45 透明度傳達 disabled，cursor 維持 pointer——刻意取捨，已記錄。

- [ ] **Step 2：在 reduced-motion 區補一行**

在 `liquid-glass.css` ~935 行（`@media (prefers-reduced-motion: reduce)` 內、`.lg-btn, .lg-tabs__pill, .lg-switch__thumb, .lg-modal__panel { transition-duration: 0.01s !important; }` 那條）後面新增一行：

```css
  .lg-check__mark, .lg-check__box { transition-duration: 0.01s !important; }
```

- [ ] **Step 3：在 `site.src.html` 元件展示加 Checkbox tile**

找到 Switch tile（`<h3>Switch</h3>` 那個 `.tile`，約 1049–1066 行，結尾是該 tile 的 `</div>`）。在其**結束 `</div>` 之後**插入新 tile：

```html
        <div class="tile lg-static lg t2">
          <div class="tile__head"><h3>Checkbox</h3></div>
          <div class="tile__stage tile__stage--col">
            <label class="lg-check">
              <input type="checkbox" checked>
              <span class="lg-check__box"><svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg></span>
              <span class="lg-check__label">記住我</span>
            </label>
            <label class="lg-check">
              <input type="checkbox">
              <span class="lg-check__box"><svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg></span>
              <span class="lg-check__label">訂閱電子報</span>
            </label>
            <label class="lg-check">
              <input type="checkbox" id="lgCheckInd">
              <span class="lg-check__box"><svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg></span>
              <span class="lg-check__label">部分選取</span>
            </label>
            <label class="lg-check">
              <input type="checkbox" disabled>
              <span class="lg-check__box"><svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg></span>
              <span class="lg-check__label">停用項目</span>
            </label>
          </div>
        </div>
```

- [ ] **Step 4：在底部 inline script 設 indeterminate**

找到填充 `data-snippet` 的 inline script（`document.querySelectorAll('[data-snippet]')…`，約 1853–1855 行）。在那段 `forEach` 之後新增：

```javascript
var _lgCInd = document.getElementById('lgCheckInd');
if (_lgCInd) _lgCInd.indeterminate = true;
```

- [ ] **Step 5：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 正常輸出、**無「缺少圖示」錯誤**（`check` 已在 icons.json）、`index.html` 重生。

- [ ] **Step 6：grep 確認產物含 checkbox**

Run: `grep -c "lg-check__box" index.html`
Expected: 數字 ≥ 4（demo 四個 box；CSS 內聯後出現更多）。

- [ ] **Step 7：Chromium 實機目視（使用者 gate）**

用 chrome-devtools / 瀏覽器開 `index.html` → 元件展示分頁，確認：
- 「記住我」預設打勾（accent 填色 + 白勾）；點擊可勾/取消，勾彈入有 overshoot。
- 「訂閱電子報」預設未勾（磨砂玻璃框）；hover 有提亮 + 微放大，按住有擠壓。
- 「部分選取」顯示白橫槓（indeterminate）；點一下轉為一般勾選態。
- 「停用項目」半透明、focus ring 出現於 keyboard focus。
- 深色主題對比 OK；非 Chromium（或關折射）走磨砂、checkbox 仍可操作、無 console 錯誤。

**交使用者檢查，核可後才進 Task 2。**

- [ ] **Step 8：Commit**

```bash
git add liquid-glass.css site.src.html index.html
git commit -m "$(printf '表單家族 A:Checkbox 元件 .lg-check(CSS + 展示)\n\n純 CSS / native checkbox,零 JS。box bespoke 磨砂(同 switch track),\nchecked/indeterminate 填 accent、白勾 overshoot 彈入、橫槓 indeterminate、\nhover/active 液態縮放、disabled 半透明、focus ring。元件展示加四態 demo。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

讓 AI 規格與「複製即用」程式碼庫涵蓋 checkbox，與既有 18 件一致。

**Files:**
- Modify: `site.src.html`（AI Guide 分頁「元件程式碼庫」加一個 `<details>` 條目；`SNIPPETS` 物件加 `check` 鍵）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段，開關那行之後加「核取方塊」一行）

**Interfaces:**
- Consumes：Task 1 定義的 class（`.lg-check` / `__box` / `__mark` / `__label`）與 demo HTML 結構。

- [ ] **Step 1：`SNIPPETS` 加 `check` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {`（~1771 行）內，緊接 `switch:` 條目之後加入（鍵名與既有風格一致、值為跳脫過的 HTML 字串）：

```javascript
  check: '<label class="lg-check">\n  <input type="checkbox" checked>\n  <span class="lg-check__box">\n    <svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg>\n  </span>\n  <span class="lg-check__label">記住我</span>\n</label>',
```

- [ ] **Step 2:「元件程式碼庫」加 Checkbox 條目**

在 `site.src.html` 程式碼庫中，找到開關條目 `<details class="acc lg-static lg"> … data-snippet="switch" … </details>`（~1413–1416 行）。在其**結束 `</details>` 之後**插入：

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">核取方塊<em>Checkbox</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="check"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md` 的「## 元件結構」段，開關那行（`開關:<label class="lg-switch">…</label>`，~123 行）之後新增：

```text
核取方塊:<label class="lg-check"><input type="checkbox"><span class="lg-check__box"><svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg></span><span class="lg-check__label">標籤</span></label>(純 CSS 零 JS;checked/indeterminate 填 accent;indeterminate 由 input.indeterminate=true 驅動;disabled 用原生屬性)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖錯誤。

Run: `grep -c "data-snippet=\"check\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫，展開「核取方塊 Checkbox」，確認顯示正確的 HTML 片段、「複製」可用。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:Checkbox 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 check 條目、程式碼庫加 Checkbox 手風琴、CLAUDE.md AI 規格書\n元件結構段補核取方塊一行。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**（對 `2026-06-21-form-controls-checkbox-design.md`）：
- 結構（label + hidden input + box + mark + label）→ Task 1 Step 3 ✓
- box bespoke 磨砂、不掛 data-lg、fallback 一併套 → Task 1 Step 1 ✓
- 狀態 unchecked/checked/indeterminate/hover/active/disabled/focus/reduced-motion → Task 1 Step 1+2 ✓
- 零 JS（demo 的 indeterminate setter 是展示用，非元件 API）→ ✓（已註明）
- 用 `#ph-check`、全 token、零新依賴 → Global Constraints ✓
- 整合位置（CSS / 展示 / CLAUDE.md / 程式碼庫 / build）→ Task 1 + Task 2 ✓
- v1 不做尺寸/error/group → 計畫未含，符合 YAGNI ✓
- 驗收清單 → Task 1 Step 7 對應逐項 ✓

**2. Placeholder scan:** 無 TBD/TODO；每個 code step 有完整程式碼；每個指令有 expected。✓

**3. Type consistency:** class 名 `.lg-check` / `__box` / `__mark` / `__label` 在 CSS、demo、snippet、CLAUDE.md、程式碼庫五處一致；`#ph-check`、`#lgCheckInd` 一致；`SNIPPETS.check` 鍵與 `data-snippet="check"` 一致。✓

**唯一刻意偏離 spec：** disabled 的 `cursor:not-allowed` 因禁用 `:has()` 而捨棄，改用 0.45 透明度傳達——已於 Task 1 Step 1 註記。
