# Stepper（`.lg-stepper`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增數字步進器 `.lg-stepper`,家族 A 第五件(#7)。

**Architecture:** 玻璃 pill 容器(`lg + data-lg` 折射)+ native `<input type="number">`(置中、隱藏原生 spinner)+ 兩端 −/+ 玻璃鈕。−/+ 由**單一委派監聽** `initSteppers()`(同 `initClearFields` 範式)呼叫 `input.stepUp/stepDown`(native clamp 在 min/max)。focus ring 保留 `.lg` 基底陰影。

**Tech Stack:** `liquid-glass.css`、`liquid-glass.js`、`site.src.html`、`CLAUDE.md`、`python3 build_site.py`。**無單元測試框架**:驗證 = build(圖示完整性 + 重生)+ grep + Chromium 目視(使用者 gate)。

## Global Constraints

- 玻璃只做容器;數字是實心內容層。容器 `.lg lg-stepper data-lg`。
- **陰影紀律(同 field)**:`.lg-stepper` 是 `.lg`,已有 `box-shadow:var(--lg-shadow)` 與 `.lg::before` inset stroke——**不重設 base box-shadow / 不重畫 inset stroke**;focus ring `:focus-within` 必須 `box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent)` **保留** base。`.lg-stepper` 僅覆寫 `border-radius` 為 pill。
- native input **不繼承 color**:`.lg-stepper__input` 須設 `color: var(--lg-text)`;固定置中寬度 `width:44px`;隱藏原生 spinner(`::-webkit-inner/outer-spin-button { -webkit-appearance:none; margin:0 }` + `appearance:textfield`)。`.lg-stepper__btn` 須設自己的 `color`(不繼承)。
- 圖示 `#ph-minus` / `#ph-plus`(已在 icons.json)引用完整字面量,**不新增圖示**。
- JS:`initSteppers()` 委派 click,`data-lg-step` 整數 `n`:`n>0`→`stepUp(n)`、`n<0`→`stepDown(-n)`;`input.disabled` 時略過;派 `input` 事件。在 `boot()` 註冊一次。
- token:`--lg-radius-pill`、`--lg-shadow`、`--lg-accent`、`--lg-tint`、`--lg-text`、`--lg-text-dim`、`--lg-font`、`--lg-speed`、`--lg-ease`、`--lg-ease-out`。不硬編顏色。
- 改完 `python3 build_site.py` 重生 `index.html`;非 Chromium 磨砂降級、−/+ 與打字純 DOM 不報錯。

---

## Task 1：`.lg-stepper` CSS + `initSteppers()` JS + 展示 demo（使用者目視 gate）

**Files:**
- Modify: `liquid-glass.css`(第 8c 節 `.lg-radio`(`.lg-radio input:disabled ~ .lg-radio__label`,第 623 行)之後、`/* 9. 滑桿 */`(第 626 行)之前插入「8d. 步進器」節;reduced-motion 區第 1159 行 `.lg-radio__box, .lg-radio__box::after` 那行之後補一行)
- Modify: `liquid-glass.js`(`initClearFields()` 函式結束 `}`(約第 807 行,`function initTooltips()` 前)之後插入 `initSteppers()`;`boot()` 內 `initClearFields();`(第 1441 行)之後加呼叫)
- Modify: `site.src.html`(元件展示 Radio tile 結束 `</div>`(第 1117 行)之後插入 Stepper tile)

**Interfaces:**
- Produces:class `.lg-stepper` / `.lg-stepper__btn` / `.lg-stepper__input`、修飾類 `.lg-stepper--disabled`、屬性 `data-lg-step`、JS 函式 `initSteppers()`。

- [ ] **Step 1：在 `liquid-glass.css` 插入 `.lg-stepper` 樣式**

在 `.lg-radio input:disabled ~ .lg-radio__label { opacity: 0.45; }`(第 623 行)之後、`/* ===== 9. 滑桿 ===== */` 註解之前,插入:

```css
/* ==================================================================== *
 * 8d. 步進器  .lg-stepper(玻璃容器 + native number + −/+ 鈕)
 * ==================================================================== */
.lg-stepper {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px;
  border-radius: var(--lg-radius-pill);
}
.lg-stepper__btn {
  flex: none;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--lg-text-dim);
  cursor: pointer;
  transition: scale var(--lg-speed) var(--lg-ease),
              background var(--lg-speed) var(--lg-ease-out),
              color var(--lg-speed) var(--lg-ease-out);
}
.lg-stepper__btn svg { width: 18px; height: 18px; fill: currentColor; }
.lg-stepper__btn:hover { background: var(--lg-tint); color: var(--lg-text); }
.lg-stepper__btn:active { scale: 0.9; }
.lg-stepper__input {
  width: 44px;
  flex: none;
  border: 0;
  background: transparent;
  outline: none;
  text-align: center;
  font: 600 15px/1 var(--lg-font);
  color: var(--lg-text);
  -moz-appearance: textfield;
  appearance: textfield;
}
.lg-stepper__input::-webkit-outer-spin-button,
.lg-stepper__input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.lg-stepper:focus-within {
  box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent);
}
.lg-stepper--disabled { opacity: 0.5; }
```

> 說明:`.lg-stepper` 是 `.lg`,border-radius 由 `.lg` 給 radius-m → 此處覆寫為 pill;**不設 base box-shadow**(沿用 `.lg` 的 `var(--lg-shadow)`);focus ring 保留 `var(--lg-shadow)`。

- [ ] **Step 2：在 reduced-motion 區補一行**

在 `liquid-glass.css` 第 1159 行 `.lg-radio__box, .lg-radio__box::after { transition-duration: 0.01s !important; }` 之後新增:

```css
  .lg-stepper__btn { transition-duration: 0.01s !important; }
```

- [ ] **Step 3：在 `liquid-glass.js` 加 `initSteppers()` 委派監聽**

(a) 在 `initClearFields()` 函式結束的 `}`(約第 807 行)之後、`function initTooltips()` 之前,插入:

```javascript
  function initSteppers() {
    document.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('[data-lg-step]') : null;
      if (!btn) return;
      var box = btn.closest('.lg-stepper');
      var input = box ? box.querySelector('.lg-stepper__input') : null;
      if (!input || input.disabled) return;
      var n = parseInt(btn.getAttribute('data-lg-step'), 10) || 0;
      if (n > 0) input.stepUp(n);
      else if (n < 0) input.stepDown(-n);
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
  }
```

(b) 在 `boot()` 內 `initClearFields();`(第 1441 行)之後加一行:

```javascript
      initSteppers();
```

- [ ] **Step 4：在 `site.src.html` 元件展示加 Stepper tile**

找到 Radio tile(`<h3>Radio</h3>`)的結束 `</div>`(第 1117 行)。在其之後插入:

```html
        <div class="tile lg-static lg t2">
          <div class="tile__head"><h3>Stepper</h3></div>
          <div class="tile__stage tile__stage--col" style="gap:14px;">
            <div class="lg lg-stepper" data-lg>
              <button type="button" class="lg-stepper__btn" data-lg-step="-1" aria-label="減少"><svg viewBox="0 0 256 256"><use href="#ph-minus"/></svg></button>
              <input class="lg-stepper__input" type="number" value="2" min="0" max="10" step="1" aria-label="數量">
              <button type="button" class="lg-stepper__btn" data-lg-step="1" aria-label="增加"><svg viewBox="0 0 256 256"><use href="#ph-plus"/></svg></button>
            </div>
            <div class="lg lg-stepper lg-stepper--disabled" data-lg>
              <button type="button" class="lg-stepper__btn" data-lg-step="-1" aria-label="減少" disabled><svg viewBox="0 0 256 256"><use href="#ph-minus"/></svg></button>
              <input class="lg-stepper__input" type="number" value="5" aria-label="數量" disabled>
              <button type="button" class="lg-stepper__btn" data-lg-step="1" aria-label="增加" disabled><svg viewBox="0 0 256 256"><use href="#ph-plus"/></svg></button>
            </div>
          </div>
        </div>
```

- [ ] **Step 5：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 「圖示引用 … 全部存在」(`minus`/`plus` 已在 icons.json,無缺圖)、`index.html` 重生。

- [ ] **Step 6：grep 確認產物**

Run: `grep -c "lg-stepper__btn" index.html`
Expected: ≥ 4(demo 四個鈕;CSS 內聯後更多)。

Run: `grep -c "data-lg-step" index.html`
Expected: ≥ 4。

Run: `grep -c "initSteppers" index.html`
Expected: ≥ 2(函式定義 + boot 呼叫)。

- [ ] **Step 7：Chromium 實機目視（使用者 gate）**

開 `index.html` → 元件展示分頁 → Stepper tile,確認:
- 點 + / − → 數字加減一步;到 max(10)/min(0)時 clamp 不再變;直接在框內打字也生效;上下鍵可調。
- 鈕 hover 提亮、按住縮一下;點進框內(或鈕)時容器顯 **accent ring**(且玻璃陰影/邊框仍在、不破玻璃)。
- 折射顯影;深色主題對比 OK。
- disabled stepper:整體淡、鈕與 input 不可動。
- 非 Chromium / 關折射:磨砂降級、−/+ 與打字正常、無 console 錯誤。

**交使用者檢查,核可後才進 Task 2。**

- [ ] **Step 8：Commit**

```bash
git add liquid-glass.css liquid-glass.js site.src.html index.html
git commit -m "$(printf '表單家族 A:Stepper .lg-stepper(CSS + JS + 展示)\n\n玻璃 pill 容器 + native number input(隱藏原生 spinner)+ −/+ 玻璃鈕;\n−/+ 由單一 initSteppers 委派(stepUp/stepDown,native clamp)。focus ring\n保留 .lg 基底陰影。元件展示加一般 + disabled 兩個。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

**Files:**
- Modify: `site.src.html`（`SNIPPETS` 加 `stepper` 鍵;程式碼庫加 `<details>` 條目）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段,單選那行之後加「步進器」一行;該行已含 `data-lg-step` 說明）

**Interfaces:**
- Consumes：Task 1 的 `.lg-stepper` / `data-lg-step` 與 demo HTML 結構。

- [ ] **Step 1：`SNIPPETS` 加 `stepper` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {` 內,緊接 `radio:` 條目(第 1892 行)之後加入:

```javascript
  stepper: '<div class="lg lg-stepper" data-lg>\n  <button type="button" class="lg-stepper__btn" data-lg-step="-1" aria-label="減少"><svg viewBox="0 0 256 256"><use href="#ph-minus"/></svg></button>\n  <input class="lg-stepper__input" type="number" value="1" min="0" max="10" step="1" aria-label="數量">\n  <button type="button" class="lg-stepper__btn" data-lg-step="1" aria-label="增加"><svg viewBox="0 0 256 256"><use href="#ph-plus"/></svg></button>\n</div>',
```

- [ ] **Step 2:「元件程式碼庫」加 Stepper 條目**

在 `site.src.html` 程式碼庫中,找到單選條目 `<details class="acc lg-static lg"> … data-snippet="radio" … </details>`(`data-snippet="radio"` 在第 1524 行)。在其結束 `</details>` 之後插入:

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">步進器<em>Stepper</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="stepper"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md`「## 元件結構」段,單選那行(`單選:<div class="lg-radio-group"…`,第 127 行)之後新增:

```text
步進器:<div class="lg lg-stepper" data-lg><button type="button" class="lg-stepper__btn" data-lg-step="-1" aria-label="減少"><svg viewBox="0 0 256 256"><use href="#ph-minus"/></svg></button><input class="lg-stepper__input" type="number" value="1" min="0" max="10" step="1"><button type="button" class="lg-stepper__btn" data-lg-step="1" aria-label="增加"><svg viewBox="0 0 256 256"><use href="#ph-plus"/></svg></button></div>(玻璃容器;值為 native number input;−/+ 由 data-lg-step 委派呼叫 stepUp/stepDown,native clamp 在 min/max;隱藏原生 spinner;disabled 加 .lg-stepper--disabled + 原生 disabled)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖。

Run: `grep -c "data-snippet=\"stepper\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫,展開「步進器 Stepper」,確認顯示正確片段、可複製。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:Stepper 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 stepper、程式碼庫加 Stepper 手風琴、CLAUDE.md AI 規格書\n元件結構段補步進器一行(含 data-lg-step 說明)。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**(對 `2026-06-22-form-controls-stepper-design.md`):
- 結構(lg lg-stepper data-lg / −鈕 / native number / +鈕)→ Task 1 Step 1+4 ✓
- 隱藏原生 spinner、input 置中/color/width → Step 1 ✓
- `initSteppers()` 委派(stepUp/stepDown、native clamp、disabled guard、派 input)+ boot 註冊 → Step 3 ✓
- 鈕 hover/active、容器 focus ring 保留 `.lg` 基底陰影、disabled 修飾類 → Step 1 ✓
- reduced-motion 補 `.lg-stepper__btn` → Step 2 ✓
- 用 `#ph-minus`/`#ph-plus` 完整字面量、無新圖示、玻璃只做容器 → Global Constraints + Step 1+4 ✓
- 整合(CSS 8d / JS / 展示 / CLAUDE.md / 程式碼庫 / build)→ Task 1 + Task 2 ✓
- YAGNI 不做 min/max 自動 disable 鈕 / 尺寸 / 長按 / 格式化 → 未含 ✓
- 驗收清單 → Step 7 對應 ✓

**2. Placeholder scan:** 無 TBD/TODO;code step 皆完整;指令有 expected。✓

**3. Type/name consistency:** `.lg-stepper`/`__btn`/`__input`/`--disabled`、`data-lg-step`、`initSteppers`、`data-snippet="stepper"`/`SNIPPETS.stepper`、`#ph-minus`/`#ph-plus` 各處一致;`initSteppers` 委派定位同容器 `.lg-stepper` 內 `.lg-stepper__input`,與 demo 結構相符;focus ring 保留 `var(--lg-shadow)`(同 field,已驗證手法)。✓
