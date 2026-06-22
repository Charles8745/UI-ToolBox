# OTP（`.lg-otp`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增驗證碼分格 `.lg-otp`,家族 A 第七件(#10)。

**Architecture:** N 個 bespoke 磨砂 `<input maxlength="1">` 格子(**非 `.lg`**,因 input 無 rim pseudo);`initOtp(container)` per-container 處理自動進格 / 退格回格清值 / 貼上分配。格子自定義 `box-shadow` + focus accent ring。**無新圖示**。

**Tech Stack:** `liquid-glass.css`、`liquid-glass.js`、`site.src.html`、`CLAUDE.md`、`python3 build_site.py`。**無單元測試框架**:驗證 = build(圖示完整性 + 重生)+ grep + Chromium 目視(使用者 gate)。

## Global Constraints

- 玻璃只做控制層;格子是 bespoke 磨砂 input(**不掛 `.lg`/`data-lg`**——input 無 `::before` rim);格子自定義 `box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft)`,focus 時加 `0 0 0 2px var(--lg-accent)`(自有陰影,不涉 `.lg` 基底)。
- token:`--lg-tint`、`--lg-stroke-soft`、`--lg-shadow-soft`、`--lg-accent`、`--lg-radius-s`、`--lg-text`、`--lg-font`、`--lg-speed`、`--lg-ease-out`。不硬編色。
- 格子 `<input type="text" inputmode="numeric" maxlength="1">`(用 `type="text"` 才支援 `maxlength`;`type="number"` 不行);第一格加 `autocomplete="one-time-code"`。
- JS `initOtp(otp)`:input 進格(多於 1 字切末字)、Backspace 在空格回上一格並清其值、paste 從第一格分配且 focus 下一空格(滿則末格)。在 `boot()` 用 `[].forEach.call(document.querySelectorAll('.lg-otp'), initOtp)` 註冊(per-container,同 `initTabs`)。
- 不做「滿格覆寫」(使用者決定:maxlength 擋住、需先 Backspace;v1 刻意行為,非缺陷)。零彙總 input、零新圖示。
- 改完 `python3 build_site.py` 重生 `index.html`;`html.lg-fallback` 一併套磨砂;非 Chromium 純 DOM 不報錯。

---

## Task 1：`.lg-otp` CSS + `initOtp()` JS + 展示 demo（使用者目視 gate）

**Files:**
- Modify: `liquid-glass.css`(第 8e 節 `.lg-rating`(`.lg-rating--disabled`,第 699 行)之後、`/* 9. 滑桿 */`(第 702 行)之前插入「8f. 驗證碼」節;reduced-motion 區第 1237 行 `.lg-rating__star` 那行之後補一行)
- Modify: `liquid-glass.js`(`initSteppers()` 函式結束 `}`(第 821 行)之後、`function initTooltips()`(第 823 行)之前插入 `initOtp()`;`boot()` 內 `[].forEach.call(document.querySelectorAll('.lg-tabs'), initTabs);`(第 1440 行)之後加一行 per-container 註冊)
- Modify: `site.src.html`(元件展示 Rating tile 結束 `</div>`(第 1153 行)之後插入 OTP tile)

**Interfaces:**
- Produces:class `.lg-otp` / `.lg-otp__cell`、JS 函式 `initOtp(container)`。

- [ ] **Step 1：在 `liquid-glass.css` 插入 `.lg-otp` 樣式**

在 `.lg-rating--disabled { opacity: 0.5; pointer-events: none; }`(第 699 行)之後、`/* ===== 9. 滑桿 ===== */` 註解之前,插入:

```css
/* ==================================================================== *
 * 8f. 驗證碼  .lg-otp(N 個 bespoke 磨砂 input;initOtp 自動進格)
 * ==================================================================== */
.lg-otp { display: inline-flex; gap: 8px; }
.lg-otp__cell {
  width: 44px;
  height: 52px;
  flex: none;
  border: 0;
  border-radius: var(--lg-radius-s);
  background: var(--lg-tint);
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft);
  text-align: center;
  font: 600 21px/1 var(--lg-font);
  color: var(--lg-text);
  outline: none;
  transition: box-shadow var(--lg-speed) var(--lg-ease-out);
}
html.lg-fallback .lg-otp__cell,
.lg-otp__cell {
  -webkit-backdrop-filter: blur(14px) saturate(1.6);
  backdrop-filter: blur(14px) saturate(1.6);
}
.lg-otp__cell:focus {
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft), 0 0 0 2px var(--lg-accent);
}
.lg-otp__cell:disabled { opacity: 0.5; cursor: not-allowed; }
```

- [ ] **Step 2：在 reduced-motion 區補一行**

在 `liquid-glass.css` 第 1237 行 `.lg-rating__star { transition-duration: 0.01s !important; }` 之後新增:

```css
  .lg-otp__cell { transition-duration: 0.01s !important; }
```

- [ ] **Step 3：在 `liquid-glass.js` 加 `initOtp()`**

(a) 在 `initSteppers()` 函式結束的 `}`(第 821 行)之後、`function initTooltips()`(第 823 行)之前,插入:

```javascript
  function initOtp(otp) {
    var cells = [].slice.call(otp.querySelectorAll('.lg-otp__cell'));
    cells.forEach(function (cell, i) {
      cell.addEventListener('input', function () {
        if (cell.value.length > 1) cell.value = cell.value.slice(-1);
        if (cell.value && cells[i + 1]) cells[i + 1].focus();
      });
      cell.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !cell.value && cells[i - 1]) {
          cells[i - 1].focus();
          cells[i - 1].value = '';
          e.preventDefault();
        }
      });
      cell.addEventListener('paste', function (e) {
        e.preventDefault();
        var data = ((e.clipboardData || window.clipboardData).getData('text') || '').replace(/\s/g, '');
        var j = 0;
        while (j < data.length && j < cells.length) { cells[j].value = data.charAt(j); j++; }
        (cells[j] || cells[cells.length - 1]).focus();
      });
    });
  }
```

(b) 在 `boot()` 內 `[].forEach.call(document.querySelectorAll('.lg-tabs'), initTabs);`(第 1440 行)之後加一行:

```javascript
      [].forEach.call(document.querySelectorAll('.lg-otp'), initOtp);
```

- [ ] **Step 4：在 `site.src.html` 元件展示加 OTP tile**

找到 Rating tile(`<h3>Rating</h3>`)的結束 `</div>`(第 1153 行)。在其之後插入:

```html
        <div class="tile lg-static lg t3">
          <div class="tile__head"><h3>OTP</h3></div>
          <div class="tile__stage tile__stage--col" style="gap:14px;">
            <div class="lg-otp" role="group" aria-label="驗證碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" autocomplete="one-time-code" aria-label="第 1 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 2 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 3 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 4 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 5 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 6 碼">
            </div>
            <div class="lg-otp" role="group" aria-label="驗證碼(停用)">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" value="4" disabled aria-label="第 1 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" value="2" disabled aria-label="第 2 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" value="8" disabled aria-label="第 3 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" value="1" disabled aria-label="第 4 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" value="9" disabled aria-label="第 5 碼">
              <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" value="6" disabled aria-label="第 6 碼">
            </div>
          </div>
        </div>
```

- [ ] **Step 5：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 「圖示引用 … 全部存在」(不需新圖示)、`index.html` 重生。

- [ ] **Step 6：grep 確認產物**

Run: `grep -c "lg-otp__cell" index.html`
Expected: ≥ 12(兩組 demo 各 6 格;CSS 內聯後更多)。

Run: `grep -c "initOtp" index.html`
Expected: ≥ 2(函式定義 + boot 呼叫)。

Run: `grep -c 'class="lg-otp"' index.html`
Expected: ≥ 2(兩組 demo)。

- [ ] **Step 7：Chromium 實機目視（使用者 gate）**

開 `index.html` → 元件展示分頁 → OTP tile,確認:
- 點第一格連打 6 碼 → 每打一碼自動跳下一格;在空格按 Backspace → 回上一格並清掉(可連續往回刪)。
- 複製一串 6 碼 → 在格子貼上 → 自動分配 6 格、focus 末格。
- 點某格 / 左右鍵可移動;focus 格顯 **accent ring**;6 格不換行、不溢出 tile。
- 第二組(disabled)半透明、不可輸入,固定顯示 428196。
- 深色主題對比 OK;非 Chromium:磨砂降級、進格/退格/貼上正常、無 console 錯誤。

**交使用者檢查,核可後才進 Task 2。**

- [ ] **Step 8：Commit**

```bash
git add liquid-glass.css liquid-glass.js site.src.html index.html
git commit -m "$(printf '表單家族 A:OTP .lg-otp(CSS + JS + 展示)\n\nN 個 bespoke 磨砂 input(maxlength=1);initOtp per-container 自動進格 /\n退格回格清值 / 貼上分配。格子非 .lg(input 無 rim),自定義 box-shadow +\nfocus ring。元件展示加一般 6 格 + disabled。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

**Files:**
- Modify: `site.src.html`（`SNIPPETS` 加 `otp` 鍵;程式碼庫加 `<details>` 條目）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段,星等評分那行之後加「驗證碼」一行）

**Interfaces:**
- Consumes：Task 1 的 `.lg-otp` / `.lg-otp__cell` 與 demo HTML 結構。

- [ ] **Step 1：`SNIPPETS` 加 `otp` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {` 內,緊接 `rating:` 條目(第 1938 行)之後加入:

```javascript
  otp: '<div class="lg-otp" role="group" aria-label="驗證碼">\n  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" autocomplete="one-time-code" aria-label="第 1 碼">\n  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 2 碼">\n  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 3 碼">\n  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 4 碼">\n  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 5 碼">\n  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 6 碼">\n</div>',
```

- [ ] **Step 2:「元件程式碼庫」加 OTP 條目**

在 `site.src.html` 程式碼庫中,找到星等評分條目 `<details class="acc lg-static lg"> … data-snippet="rating" … </details>`(`data-snippet="rating"` 在第 1568 行)。在其結束 `</details>` 之後插入:

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">驗證碼<em>OTP</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="otp"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md`「## 元件結構」段,星等評分那行(`星等評分:<div class="lg-rating"…`,第 129 行)之後新增:

```text
驗證碼:<div class="lg-otp" role="group"><input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" autocomplete="one-time-code">…(共 6 格 input)…</div>(N 個磨砂 input;initOtp 自動進格 / 退格回上一格並清值 / 貼上從第一格分配;值由各 .lg-otp__cell 串接;type 用 text 才支援 maxlength;disabled 用原生屬性)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖。

Run: `grep -c "data-snippet=\"otp\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫,展開「驗證碼 OTP」,確認顯示正確片段、可複製。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:OTP 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 otp、程式碼庫加 OTP 手風琴、CLAUDE.md AI 規格書\n元件結構段補驗證碼一行。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**(對 `2026-06-22-form-controls-otp-design.md`):
- 結構(.lg-otp role=group / N 個 .lg-otp__cell input maxlength=1 inputmode=numeric / 第一格 autocomplete=one-time-code)→ Task 1 Step 1+4 ✓
- bespoke 磨砂 input(非 .lg)、focus ring 自有陰影、disabled `:disabled`、reduced-motion → Step 1+2 ✓
- initOtp 三行為(進格 / backspace 回格清值 / paste 分配)+ boot per-container 註冊 → Step 3 ✓
- 不做滿格覆寫(刻意)、零彙總 input、零新圖示、token 不硬編 → Global Constraints + Step 1+3 ✓
- 整合(CSS 8f / JS / 展示 / CLAUDE.md / 程式碼庫 / build)→ Task 1 + Task 2 ✓
- YAGNI 不做倒數/重送/遮罩/驗證 → 未含 ✓
- 驗收清單 → Step 7 對應 ✓

**2. Placeholder scan:** 無 TBD/TODO;code step 皆完整;指令有 expected。✓

**3. Type/name consistency:** `.lg-otp`/`__cell`、`initOtp`、`data-snippet="otp"`/`SNIPPETS.otp` 各處一致;`initOtp` 取 `.lg-otp__cell` 與 demo 結構相符;boot per-container 註冊同 `initTabs` 範式;格子 `type="text"`(支援 maxlength)、focus ring 用格子自有 `var(--lg-shadow-soft)`(非 `.lg` 基底,無繼承問題)。✓
