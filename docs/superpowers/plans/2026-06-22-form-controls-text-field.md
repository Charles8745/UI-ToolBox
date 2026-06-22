# Text field（`.lg-field`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增浮動標籤單行文字輸入 `.lg-field`,家族 A 第二件。

**Architecture:** 玻璃只在 `__box`(`lg + data-lg` 折射,同 `.lg-search`);floating label 純 CSS(`placeholder=" "` + `:placeholder-shown`/`:focus` 切換,只動 transform+color);清除鈕顯隱純 CSS,點擊動作由 `liquid-glass.js` 的**單一** `[data-lg-clear]` 委派監聽處理(本元件唯一 JS,沿用既有 `initModals` 委派範式)。狀態 focus/error/disabled 走 `:focus-within` 與修飾類。

**Tech Stack:** `liquid-glass.css`、`liquid-glass.js`、`site.src.html`、`CLAUDE.md`、`python3 build_site.py`。**無單元測試框架**:驗證 = build(圖示完整性 + 重生)+ grep + Chromium 目視(使用者 gate)。

## Global Constraints

- 玻璃只做控制層;label / hint / 使用者輸入的字是實心內容層。玻璃只在 `.lg-field__box`(`lg + data-lg`)。
- 顏色/圓角/字型用既有 token,不硬編。token 值:`--lg-radius-m`=20px、`--lg-accent`、`--lg-down`=#d2503e、`--lg-tint`、`--lg-stroke`=0.50、`--lg-stroke-soft`=0.22、`--lg-shadow-soft`、`--lg-text`、`--lg-text-dim`、`--lg-font`、`--lg-speed`=0.34s、`--lg-ease-out`=cubic-bezier(0.22,0.8,0.3,1)。
- `placeholder` **必須是一個空格 `" "`**(floating 機制靠 `:placeholder-shown`)。
- **不引入 `:has()`**:disabled 用修飾類 `.lg-field--disabled`;readonly v1 僅淡化文字、不特判 focus ring(刻意簡化,記錄)。
- 圖示 `#ph-x`(已在 icons.json)引用完整字面量 `'#ph-x'`,不新增圖示。
- label 與 input 是相鄰 `+`(DOM 順序 input→label);清除鈕在 input 之後(一般兄弟 `~`)。
- 改完 `python3 build_site.py` 重生 `index.html`;非 Chromium 走磨砂降級,清除/floating 純 DOM 不報錯。

---

## Task 1：`.lg-field` CSS + 清除鈕 JS + 展示 demo（使用者目視 gate）

交付「可在 Chromium 操作的浮動標籤輸入框」。CSS + JS(清除動作)+ demo 綁一起,否則清除鈕無從測、floating 無從看。

**Files:**
- Modify: `liquid-glass.css`(第 7 節 `.lg-search`(~322–348 行)之後插入「7b. 文字輸入」節;~935 行 reduced-motion 區補一行)
- Modify: `liquid-glass.js`(`initModals()` 函式結束(~794 行 `}`)之後插入 `initClearFields()`;`boot()` 內 `initScrollEdge();`(~1427 行)之後加一行呼叫)
- Modify: `site.src.html`(元件展示 Checkbox tile 之後插入 Text field tile)

**Interfaces:**
- Produces(後續 Task 2 與使用者引用的固定名稱):class `.lg-field` / `.lg-field__box` / `.lg-field__input` / `.lg-field__label` / `.lg-field__clear` / `.lg-field__hint`、修飾類 `.lg-field--error` / `.lg-field--disabled`、屬性 `data-lg-clear`、JS 函式 `initClearFields()`。

- [ ] **Step 1：在 `liquid-glass.css` 插入 `.lg-field` 樣式**

在第 7 節 `.lg-search kbd { … }` 區塊結束(約第 348 行 `}`)之後、`/* 8. 開關 */` 註解之前,插入:

```css
/* ==================================================================== *
 * 7b. 文字輸入  .lg-field(浮動標籤;玻璃只在 __box,label/hint 為實心內容)
 * ==================================================================== */
.lg-field { display: flex; flex-direction: column; gap: 6px; }
.lg-field__box {
  position: relative;
  display: flex;
  align-items: stretch;
  min-height: 58px;
  padding: 0 14px;
  border-radius: var(--lg-radius-m);
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft);
  transition: box-shadow var(--lg-speed) var(--lg-ease-out);
}
.lg-field__box:hover { box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke); }
.lg-field__input {
  flex: 1;
  min-width: 0;
  border: 0;
  background: transparent;
  outline: none;
  font: 400 15px/1.2 var(--lg-font);
  color: var(--lg-text);
  padding: 24px 0 6px;
}
.lg-field__label {
  position: absolute;
  left: 14px;
  top: 0;
  height: 100%;
  display: flex;
  align-items: center;
  font: 400 15px/1 var(--lg-font);
  color: var(--lg-text-dim);
  pointer-events: none;
  transform-origin: left center;
  transition: transform var(--lg-speed) var(--lg-ease-out), color var(--lg-speed) var(--lg-ease-out);
}
.lg-field__input:focus + .lg-field__label,
.lg-field__input:not(:placeholder-shown) + .lg-field__label {
  transform: translateY(-16px) scale(.78);
  color: var(--lg-accent);
}
.lg-field__box:focus-within {
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft), 0 0 0 2px var(--lg-accent);
}
.lg-field__clear {
  flex: none;
  align-self: center;
  width: 24px;
  height: 24px;
  margin-left: 8px;
  padding: 0;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--lg-text-dim);
  cursor: pointer;
  transition: color var(--lg-speed) var(--lg-ease-out), background var(--lg-speed) var(--lg-ease-out);
}
.lg-field__clear svg { width: 15px; height: 15px; fill: currentColor; }
.lg-field__clear:hover { color: var(--lg-text); background: var(--lg-tint); }
.lg-field__input:placeholder-shown ~ .lg-field__clear { display: none; }
.lg-field__hint { font: 400 12.5px/1.3 var(--lg-font); color: var(--lg-text-dim); padding: 0 4px; }
.lg-field--error .lg-field__box,
.lg-field--error .lg-field__box:focus-within {
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft), 0 0 0 2px var(--lg-down);
}
.lg-field--error .lg-field__input + .lg-field__label { color: var(--lg-down); }
.lg-field--error .lg-field__hint { color: var(--lg-down); }
.lg-field--disabled .lg-field__box { opacity: .5; }
.lg-field--disabled .lg-field__input { cursor: not-allowed; }
.lg-field__input:read-only { color: var(--lg-text-dim); }
```

> 說明:error 的兩條 box 規則寫在 `:focus-within` 之後且特異度 ≥,確保「errored 且聚焦」仍顯紅。readonly 僅淡化文字、不特判 ring(避開 `:has()`,刻意簡化)。

- [ ] **Step 2：在 reduced-motion 區補一行**

在 `liquid-glass.css` ~935 行 `@media (prefers-reduced-motion: reduce)` 內、`.lg-btn, .lg-tabs__pill, .lg-switch__thumb, .lg-modal__panel { … }` 那條之後(若已有 `.lg-check__mark, .lg-check__box` 那行則接在它後)新增:

```css
  .lg-field__label { transition-duration: 0.01s !important; }
```

- [ ] **Step 3：在 `liquid-glass.js` 加清除鈕委派監聽**

(a) 在 `initModals()` 函式結束的 `}`(約第 794 行)之後、`function initTooltips()`(約第 796 行)之前,插入新函式:

```javascript
  function initClearFields() {
    document.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('[data-lg-clear]') : null;
      if (!btn) return;
      var box = btn.closest('.lg-field__box');
      var input = box ? box.querySelector('.lg-field__input') : null;
      if (!input) return;
      input.value = '';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.focus();
    });
  }
```

(b) 在 `boot()` 內 `initScrollEdge();`(約第 1427 行)之後加一行:

```javascript
      initClearFields();
```

- [ ] **Step 4：在 `site.src.html` 元件展示加 Text field tile**

找到 Checkbox tile(`<h3>Checkbox</h3>` 那個 `.tile`)的結束 `</div>`(約第 1089 行),在其之後插入:

```html
        <div class="tile lg-static lg t2">
          <div class="tile__head"><h3>Text field</h3></div>
          <div class="tile__stage tile__stage--col" style="align-items:stretch;gap:14px;">
            <div class="lg-field">
              <div class="lg lg-field__box" data-lg>
                <input id="tf-email" class="lg-field__input" type="email" placeholder=" ">
                <label for="tf-email" class="lg-field__label">電子郵件</label>
                <button type="button" class="lg-field__clear" data-lg-clear aria-label="清除"><svg viewBox="0 0 256 256"><use href="#ph-x"/></svg></button>
              </div>
              <span class="lg-field__hint">我們不會分享你的信箱</span>
            </div>
            <div class="lg-field lg-field--error">
              <div class="lg lg-field__box" data-lg>
                <input id="tf-err" class="lg-field__input" type="text" placeholder=" " value="not-an-email">
                <label for="tf-err" class="lg-field__label">帳號</label>
                <button type="button" class="lg-field__clear" data-lg-clear aria-label="清除"><svg viewBox="0 0 256 256"><use href="#ph-x"/></svg></button>
              </div>
              <span class="lg-field__hint">請輸入有效的帳號</span>
            </div>
            <div class="lg-field lg-field--disabled">
              <div class="lg lg-field__box" data-lg>
                <input id="tf-dis" class="lg-field__input" type="text" placeholder=" " value="已鎖定" disabled>
                <label for="tf-dis" class="lg-field__label">停用欄位</label>
              </div>
            </div>
          </div>
        </div>
```

- [ ] **Step 5：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 「圖示引用 … 全部存在」(`x` 已在 icons.json,無缺圖)、`index.html` 重生。

- [ ] **Step 6：grep 確認產物**

Run: `grep -c "lg-field__box" index.html`
Expected: ≥ 3(demo 三個框;CSS 內聯後更多)。

Run: `grep -c "data-lg-clear" index.html`
Expected: ≥ 2。

Run: `grep -c "initClearFields" index.html`
Expected: ≥ 2(函式定義 + boot 呼叫)。

- [ ] **Step 7：Chromium 實機目視（使用者 gate）**

開 `index.html` → 元件展示分頁 → Text field tile,確認:
- 「電子郵件」空欄:label 置中如 placeholder;點擊聚焦 → label **平滑上浮轉 accent**、框顯 **accent ring**;打字 → **清除鈕出現**;點清除 → 清空、input 重新聚焦、不報錯。
- 「帳號」(error):框 / label / hint 轉**紅**(`--lg-down`);聚焦時仍維持紅。
- 「停用欄位」(disabled):整框淡化、not-allowed,label 呈上浮淡態。
- 折射:框在折射(若顯影偏淡,記下,可後續疊圖像背景——B6 課題)。深色主題對比 OK。
- 非 Chromium / 關折射:磨砂降級、floating 與清除動作正常、無 console 錯誤。

**交使用者檢查,核可後才進 Task 2。**

- [ ] **Step 8：Commit**

```bash
git add liquid-glass.css liquid-glass.js site.src.html index.html
git commit -m "$(printf '表單家族 A:Text field 元件 .lg-field(CSS + JS + 展示)\n\n浮動標籤單行輸入:玻璃折射框(同 search)、純 CSS floating label\n(placeholder=空格 + :placeholder-shown/:focus)、清除鈕(顯隱純 CSS,\n點擊由單一 data-lg-clear 委派監聽)、focus(accent ring)/error(--lg-down)/\ndisabled(修飾類)/readonly。元件展示加三態 demo。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

**Files:**
- Modify: `site.src.html`（`SNIPPETS` 物件加 `field` 鍵;程式碼庫加 `<details>` 條目）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段,搜尋那行之後加「文字輸入」一行）

**Interfaces:**
- Consumes：Task 1 的 class 與 demo HTML 結構、`data-lg-clear`、`#ph-x`。

- [ ] **Step 1：`SNIPPETS` 加 `field` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {` 內,緊接 `search:` 條目之後加入:

```javascript
  field: '<div class="lg-field">\n  <div class="lg lg-field__box" data-lg>\n    <input id="f1" class="lg-field__input" type="email" placeholder=" ">\n    <label for="f1" class="lg-field__label">電子郵件</label>\n    <button type="button" class="lg-field__clear" data-lg-clear aria-label="清除"><svg viewBox="0 0 256 256"><use href="#ph-x"/></svg></button>\n  </div>\n  <span class="lg-field__hint">我們不會分享你的信箱</span>\n</div>',
```

- [ ] **Step 2:「元件程式碼庫」加 Text field 條目**

在 `site.src.html` 程式碼庫中,找到搜尋條目 `<details class="acc lg-static lg"> … data-snippet="search" … </details>`(約第 1421–1424 行)。在其結束 `</details>` 之後插入:

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">文字輸入<em>Text field</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="field"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md`「## 元件結構」段,搜尋那行(`搜尋:<div class="lg lg-search"…`)之後新增:

```text
文字輸入:<div class="lg-field"><div class="lg lg-field__box" data-lg><input id="f1" class="lg-field__input" placeholder=" "><label for="f1" class="lg-field__label">標籤</label><button type="button" class="lg-field__clear" data-lg-clear aria-label="清除"><svg viewBox="0 0 256 256"><use href="#ph-x"/></svg></button></div><span class="lg-field__hint">說明</span></div>(浮動標籤純 CSS;placeholder 必須是一個空格 " ";清除鈕點擊由 data-lg-clear 委派處理;error 加 .lg-field--error、disabled 加 .lg-field--disabled、readonly 用原生屬性)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖。

Run: `grep -c "data-snippet=\"field\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫,展開「文字輸入 Text field」,確認顯示正確片段、可複製。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:Text field 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 field、程式碼庫加 Text field 手風琴、CLAUDE.md AI 規格書\n元件結構段補文字輸入一行。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**(對 `2026-06-22-form-controls-text-field-design.md`):
- 結構(.lg-field / __box(lg+data-lg) / __input / __label(for) / __clear / __hint)→ Task 1 Step 1+4 ✓
- floating label 純 CSS(placeholder=" "、:placeholder-shown/:focus、相鄰 +、只動 transform+color)→ Step 1 ✓
- 清除鈕顯隱純 CSS(`:placeholder-shown ~`)+ 點擊委派(initClearFields,清空/派 input 事件/refocus)→ Step 1 + Step 3 ✓
- 狀態 hover/focus(:focus-within accent ring 保留 base)/error(--lg-down 壓過 focus)/disabled(修飾類)/readonly(淡字)/reduced-motion → Step 1 + Step 2 ✓
- 玻璃只在 __box、token、#ph-x 完整字面量、不引入 :has() → Global Constraints + Step 1 ✓
- 整合(CSS 7b / JS / 展示 / CLAUDE.md / 程式碼庫 / build)→ Task 1 + Task 2 ✓
- YAGNI 不做 leading icon / 尺寸 / label-less / Textarea → 計畫未含,符合 ✓
- 驗收清單 → Step 7 對應 ✓

**2. Placeholder scan:** 無 TBD/TODO;每個 code step 有完整程式碼;每個指令有 expected。✓

**3. Type/name consistency:** `.lg-field` 系列 class、`data-lg-clear`、`initClearFields`、`#ph-x`、`data-snippet="field"`/`SNIPPETS.field` 在 CSS / JS / demo / snippet / accordion / CLAUDE.md 各處一致;DOM 順序 input→label(相鄰 +)、clear 在 input 之後(~)與選擇器相符。✓

**刻意偏離 spec(記錄):** readonly 僅淡化文字、不特判 focus ring(乾淨做法需 `:has()`,專案禁用)——同 Checkbox 的避 :has() 取捨。
