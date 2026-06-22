# Radio group（`.lg-radio` / `.lg-radio-group`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增單選 `.lg-radio` + 薄版型包裹 `.lg-radio-group`,家族 A 第四件(#6),平行 `.lg-check`。

**Architecture:** 純 CSS + native `<input type="radio">`,**零 JS**(同 `.lg-check`)。圓形磨砂 box + 中心白圓點(`::after`,無圖示);checked 填 `--lg-accent` + 圓點彈入。狀態/磨砂手法/token 全平行 checkbox,僅 box 圓化、標記改 `::after` 圓點、無 indeterminate。

**Tech Stack:** `liquid-glass.css`、`site.src.html`、`CLAUDE.md`、`python3 build_site.py`。**無單元測試框架**:驗證 = build(圖示完整性 + 重生)+ grep + Chromium 目視(使用者 gate)。

## Global Constraints

- 玻璃只做控制層;圓點/字是實心內容層。`.lg-radio__box` 用 bespoke 磨砂(`backdrop-filter`),**不掛 `data-lg`**,不需 `attach()`。
- 顏色/圓角/字型用既有 token,不硬編(白圓點用 `#fff`,同 checkbox 標記)。token:`--lg-tint`、`--lg-stroke`=0.50、`--lg-stroke-soft`=0.22、`--lg-shadow-soft`、`--lg-accent`、`--lg-text`、`--lg-font`、`--lg-speed`=0.34s、`--lg-ease`、`--lg-ease-out`;圓點 overshoot 用 `cubic-bezier(.34,1.56,.64,1)`(同 checkbox 勾)。
- **不引入 `:has()`**:disabled 用兄弟選擇器 `input:disabled ~ .lg-radio__box / __label`。
- **零新圖示**(圓點純 CSS `::after`);**零新 JS**。
- DOM 順序 input→box→label;box 用相鄰 `+`、label/box disabled 用一般兄弟 `~`。
- 改完 `python3 build_site.py` 重生 `index.html`;`html.lg-fallback` 一併套磨砂;非 Chromium native radio 正常、不報錯。

---

## Task 1：`.lg-radio` CSS + 展示 demo（使用者目視 gate）

**Files:**
- Modify: `liquid-glass.css`(第 8b 節 `.lg-check` 結束(`.lg-check input:disabled ~ .lg-check__label`,第 563 行)之後、`/* 9. 滑桿 */`(第 566 行)之前插入「8c. 單選」節;reduced-motion 區第 1098 行 `.lg-check__mark, .lg-check__box` 那行之後補一行)
- Modify: `site.src.html`(元件展示 Checkbox tile 結束 `</div>`(第 1089 行)之後插入 Radio tile)

**Interfaces:**
- Produces:class `.lg-radio` / `.lg-radio-group` / `.lg-radio__box` / `.lg-radio__label`(供 Task 2 與使用者引用)。

- [ ] **Step 1：在 `liquid-glass.css` 插入 `.lg-radio` 樣式**

在 `.lg-check input:disabled ~ .lg-check__label { opacity: 0.45; }`(第 563 行)之後、`/* ===== 9. 滑桿 ===== */` 註解之前,插入:

```css
/* ==================================================================== *
 * 8c. 單選  .lg-radio(純 CSS,radio;圓 box + 中心圓點,點為實心內容)
 * ==================================================================== */
.lg-radio-group { display: flex; flex-direction: column; gap: 12px; }
.lg-radio {
  display: inline-flex;
  align-items: center;
  gap: 11px;
  cursor: pointer;
  font: 500 14px/1 var(--lg-font);
  color: var(--lg-text);
  user-select: none;
}
.lg-radio input { position: absolute; opacity: 0; width: 0; height: 0; }
.lg-radio__box {
  position: relative;
  width: 22px;
  height: 22px;
  flex: none;
  border-radius: 50%;
  background: var(--lg-tint);
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft);
  transition: background var(--lg-speed) var(--lg-ease-out),
              box-shadow var(--lg-speed) var(--lg-ease-out),
              scale var(--lg-speed) var(--lg-ease);
}
html.lg-fallback .lg-radio__box,
.lg-radio__box {
  -webkit-backdrop-filter: blur(14px) saturate(1.6);
  backdrop-filter: blur(14px) saturate(1.6);
}
.lg-radio__box::after {
  content: "";
  position: absolute;
  inset: 0;
  margin: auto;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
  scale: 0;
  transition: scale var(--lg-speed) cubic-bezier(.34, 1.56, .64, 1);
}
.lg-radio:hover .lg-radio__box {
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke);
  scale: 1.04;
}
.lg-radio:active .lg-radio__box { scale: 0.92; }
.lg-radio input:checked + .lg-radio__box {
  background: var(--lg-accent);
  box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px transparent;
}
.lg-radio input:checked + .lg-radio__box::after { scale: 1; }
.lg-radio input:focus-visible + .lg-radio__box {
  outline: 2px solid var(--lg-accent);
  outline-offset: 3px;
}
.lg-radio input:disabled ~ .lg-radio__box,
.lg-radio input:disabled ~ .lg-radio__label { opacity: 0.45; }
```

- [ ] **Step 2：在 reduced-motion 區補一行**

在 `liquid-glass.css` 第 1098 行 `.lg-check__mark, .lg-check__box { transition-duration: 0.01s !important; }` 之後新增:

```css
  .lg-radio__box, .lg-radio__box::after { transition-duration: 0.01s !important; }
```

- [ ] **Step 3：在 `site.src.html` 元件展示加 Radio tile**

找到 Checkbox tile(`<h3>Checkbox</h3>`)的結束 `</div>`(第 1089 行)。在其之後插入:

```html
        <div class="tile lg-static lg t2">
          <div class="tile__head"><h3>Radio</h3></div>
          <div class="tile__stage tile__stage--col" style="align-items:flex-start;">
            <div class="lg-radio-group" role="radiogroup" aria-label="方案">
              <label class="lg-radio">
                <input type="radio" name="lg-demo-plan" value="free" checked>
                <span class="lg-radio__box"></span>
                <span class="lg-radio__label">免費方案</span>
              </label>
              <label class="lg-radio">
                <input type="radio" name="lg-demo-plan" value="pro">
                <span class="lg-radio__box"></span>
                <span class="lg-radio__label">專業方案</span>
              </label>
              <label class="lg-radio">
                <input type="radio" name="lg-demo-plan" value="team">
                <span class="lg-radio__box"></span>
                <span class="lg-radio__label">團隊方案</span>
              </label>
              <label class="lg-radio">
                <input type="radio" name="lg-demo-plan" value="ent" disabled>
                <span class="lg-radio__box"></span>
                <span class="lg-radio__label">企業方案(停用)</span>
              </label>
            </div>
          </div>
        </div>
```

- [ ] **Step 4：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 「圖示引用 … 全部存在」(不需新圖示)、`index.html` 重生。

- [ ] **Step 5：grep 確認產物**

Run: `grep -c "lg-radio__box" index.html`
Expected: ≥ 4(demo 四個 box;CSS 內聯後更多)。

Run: `grep -c "lg-radio-group" index.html`
Expected: ≥ 2(CSS 規則 + demo group)。

Run: `grep -c 'type="radio"' index.html`
Expected: ≥ 4。

- [ ] **Step 6：Chromium 實機目視（使用者 gate）**

開 `index.html` → 元件展示分頁 → Radio tile,確認:
- 預設「免費方案」選中(accent 填 + 白圓點);點別的選項 → 圓點彈入該項、原選項自動取消(native 單選)。
- 四個 radio 左緣對齊成一列;方向鍵可在組內移動選取。
- 「企業方案(停用)」半透明、不可選;keyboard focus 有 ring;hover/active 有縮放回饋。
- 深色主題對比 OK;非 Chromium / 關折射:磨砂降級、native radio 正常、無 console 錯誤。

**交使用者檢查,核可後才進 Task 2。**

- [ ] **Step 7：Commit**

```bash
git add liquid-glass.css site.src.html index.html
git commit -m "$(printf '表單家族 A:Radio group .lg-radio(CSS + 展示)\n\n平行 .lg-check:純 CSS / native radio,圓形磨砂 box + 中心白圓點\n(::after,scale overshoot),checked 填 accent。附 .lg-radio-group 薄版型。\n元件展示加一組四選項(含 disabled)。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

**Files:**
- Modify: `site.src.html`（`SNIPPETS` 加 `radio` 鍵;程式碼庫加 `<details>` 條目）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段,核取方塊那行之後加「單選」一行）

**Interfaces:**
- Consumes：Task 1 的 `.lg-radio` / `.lg-radio-group` 與 demo HTML 結構。

- [ ] **Step 1：`SNIPPETS` 加 `radio` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {` 內,緊接 `check:` 條目(第 1859 行)之後加入:

```javascript
  radio: '<div class="lg-radio-group" role="radiogroup" aria-label="方案">\n  <label class="lg-radio">\n    <input type="radio" name="plan" value="free" checked>\n    <span class="lg-radio__box"></span>\n    <span class="lg-radio__label">免費方案</span>\n  </label>\n  <label class="lg-radio">\n    <input type="radio" name="plan" value="pro">\n    <span class="lg-radio__box"></span>\n    <span class="lg-radio__label">專業方案</span>\n  </label>\n</div>',
```

- [ ] **Step 2:「元件程式碼庫」加 Radio 條目**

在 `site.src.html` 程式碼庫中,找到核取方塊條目 `<details class="acc lg-static lg"> … data-snippet="check" … </details>`(`data-snippet="check"` 在第 1492 行)。在其結束 `</details>` 之後插入:

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">單選<em>Radio</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="radio"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md`「## 元件結構」段,核取方塊那行(`核取方塊:<label class="lg-check">…`,第 126 行)之後新增:

```text
單選:<div class="lg-radio-group" role="radiogroup"><label class="lg-radio"><input type="radio" name="g" value="a" checked><span class="lg-radio__box"></span><span class="lg-radio__label">標籤</span></label><label class="lg-radio"><input type="radio" name="g" value="b"><span class="lg-radio__box"></span><span class="lg-radio__label">標籤</span></label></div>(純 CSS 零 JS;圓 box + 中心圓點;同組共用 name 即單選;disabled 用原生屬性;無 indeterminate)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖。

Run: `grep -c "data-snippet=\"radio\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫,展開「單選 Radio」,確認顯示正確片段、可複製。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:Radio 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 radio、程式碼庫加 Radio 手風琴、CLAUDE.md AI 規格書\n元件結構段補單選一行。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**(對 `2026-06-22-form-controls-radio-design.md`):
- 結構(.lg-radio-group / .lg-radio / __box / __label,label 包 hidden radio)→ Task 1 Step 1+3 ✓
- box 圓化(border-radius:50%)+ 中心圓點(::after,8px,白,overshoot)→ Step 1 ✓
- checked 填 accent + 圓點 scale 1;hover/active/disabled/focus/reduced-motion 平行 checkbox → Step 1+2 ✓
- 零 JS、零新圖示、bespoke 磨砂不掛 data-lg、不引入 :has()、無 indeterminate → Global Constraints + Step 1 ✓
- group 薄版型(flex column gap)+ role=radiogroup → Step 1(CSS)+ Step 3(demo)✓
- 整合(CSS 8c / 展示 / CLAUDE.md / 程式碼庫 / build)→ Task 1 + Task 2 ✓
- YAGNI 不做尺寸/卡片式/水平預設 → 未含 ✓
- 驗收清單 → Step 6 對應 ✓

**2. Placeholder scan:** 無 TBD/TODO;code step 皆完整;指令有 expected。✓

**3. Type/name consistency:** `.lg-radio`/`-group`/`__box`/`__label`、`data-snippet="radio"`/`SNIPPETS.radio`、demo `name="lg-demo-plan"`(頁面唯一)各處一致;DOM 順序 input→box→label 與選擇器(`+` box、`~` disabled)相符;圓點 `::after` 與 checkbox 的 `::after`(indeterminate bar)不同類、無衝突。✓
