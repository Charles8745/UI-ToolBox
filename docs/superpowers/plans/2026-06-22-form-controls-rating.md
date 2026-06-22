# Rating（`.lg-rating`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增 5 星評分 `.lg-rating`,家族 A 第六件(#9)。

**Architecture:** 純 CSS + native `<input type="radio">`,**零 JS**。星 5→1 DOM 倒序 + `flex-direction:row-reverse`(視覺正序);`~` 選擇器做 hover 預覽 + 已選高亮。單一 `#ph-star-fill` 以 `currentColor` 變色(off=dim、on=accent)。星是實心內容層(**非玻璃**)。

**Tech Stack:** `liquid-glass.css`、`site.src.html`、`CLAUDE.md`、`python3 build_site.py`。**無單元測試框架**:驗證 = build(圖示完整性 + 重生)+ grep + Chromium 目視(使用者 gate)。

## Global Constraints

- 星是實心內容層的圖示(像儀表板數字),**rating 不上玻璃**;玻璃只在外層 demo tile。
- **CSS 四條 cascade 規則的順序與寫法必須照抄**(否則 hover 預覽錯亂):base dim → `input:checked ~ label`(accent)→ `:hover input ~ label`(reset dim)→ `:hover label:hover` / `:hover label:hover ~ label`(preview accent)。推導見 spec:規則 3(0,2,2)在規則 2(0,2,2)之後 → reset 勝 checked;規則 4(0,3,1/0,3,2)> 規則 3 → preview 勝 reset。
- 星 5→1 **DOM 倒序**,容器 `flex-direction:row-reverse`;每星 = `<input type=radio>` 緊接其 `<label class="lg-rating__star">`。radio 隱藏(`position:absolute;opacity:0;width:0;height:0`),仍可鍵盤聚焦。
- 圖示 `#ph-star-fill`(已在 icons.json)引用完整字面量,**無新圖示**;`fill: currentColor`。
- **不引入 `:has()`、零 JS**。color 用 token(off `--lg-text-dim`、on `--lg-accent`),不硬編。
- disabled:`.lg-rating--disabled { opacity:.5; pointer-events:none }`(demo 同時對 radio 加 native `disabled`)。
- 改完 `python3 build_site.py` 重生 `index.html`;星純 DOM/CSS、無折射依賴,非 Chromium 正常。

---

## Task 1：`.lg-rating` CSS + 展示 demo（使用者目視 gate）

**Files:**
- Modify: `liquid-glass.css`(第 8d 節 `.lg-stepper`(`.lg-stepper--disabled`,第 670 行)之後、`/* 9. 滑桿 */`(第 673 行)之前插入「8e. 星等評分」節;reduced-motion 區第 1207 行 `.lg-stepper__btn` 那行之後補一行)
- Modify: `site.src.html`(元件展示 Stepper tile 結束 `</div>`(第 1133 行)之後插入 Rating tile)

**Interfaces:**
- Produces:class `.lg-rating` / `.lg-rating__star`、修飾類 `.lg-rating--disabled`。

- [ ] **Step 1：在 `liquid-glass.css` 插入 `.lg-rating` 樣式**

在 `.lg-stepper--disabled { opacity: 0.5; }`(第 670 行)之後、`/* ===== 9. 滑桿 ===== */` 註解之前,插入:

```css
/* ==================================================================== *
 * 8e. 星等評分  .lg-rating(純 CSS,radio;reverse DOM + ~ 選擇器,星非玻璃)
 * ==================================================================== */
.lg-rating {
  display: inline-flex;
  flex-direction: row-reverse;
  gap: 2px;
}
.lg-rating input { position: absolute; opacity: 0; width: 0; height: 0; }
.lg-rating__star {
  display: inline-flex;
  cursor: pointer;
  color: var(--lg-text-dim);
  transition: color var(--lg-speed) var(--lg-ease-out),
              scale var(--lg-speed) var(--lg-ease);
}
.lg-rating__star svg { width: 28px; height: 28px; fill: currentColor; }
/* 2. 已選及更低星 → accent */
.lg-rating input:checked ~ label { color: var(--lg-accent); }
/* 3. 容器 hover 時全部重置 dim(特異度同規則 2、置於其後 → 勝出) */
.lg-rating:hover input ~ label { color: var(--lg-text-dim); }
/* 4. hover 預覽:hovered + 更低星 → accent(特異度高於規則 3 → 勝出);hovered 彈一下 */
.lg-rating:hover label:hover,
.lg-rating:hover label:hover ~ label { color: var(--lg-accent); }
.lg-rating:hover label:hover { scale: 1.12; }
/* focus / disabled */
.lg-rating input:focus-visible + label { outline: 2px solid var(--lg-accent); outline-offset: 2px; }
.lg-rating--disabled { opacity: 0.5; pointer-events: none; }
```

- [ ] **Step 2：在 reduced-motion 區補一行**

在 `liquid-glass.css` 第 1207 行 `.lg-stepper__btn { transition-duration: 0.01s !important; }` 之後新增:

```css
  .lg-rating__star { transition-duration: 0.01s !important; }
```

- [ ] **Step 3：在 `site.src.html` 元件展示加 Rating tile**

找到 Stepper tile(`<h3>Stepper</h3>`)的結束 `</div>`(第 1133 行)。在其之後插入:

```html
        <div class="tile lg-static lg t2">
          <div class="tile__head"><h3>Rating</h3></div>
          <div class="tile__stage tile__stage--col" style="gap:14px;">
            <div class="lg-rating" role="radiogroup" aria-label="評分">
              <input type="radio" name="lg-demo-rate" id="lgrate5" value="5"><label for="lgrate5" class="lg-rating__star" aria-label="5 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate" id="lgrate4" value="4" checked><label for="lgrate4" class="lg-rating__star" aria-label="4 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate" id="lgrate3" value="3"><label for="lgrate3" class="lg-rating__star" aria-label="3 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate" id="lgrate2" value="2"><label for="lgrate2" class="lg-rating__star" aria-label="2 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate" id="lgrate1" value="1"><label for="lgrate1" class="lg-rating__star" aria-label="1 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
            </div>
            <div class="lg-rating lg-rating--disabled" role="radiogroup" aria-label="評分(停用)">
              <input type="radio" name="lg-demo-rate2" id="lgrated5" value="5" disabled><label for="lgrated5" class="lg-rating__star" aria-label="5 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate2" id="lgrated4" value="4" disabled><label for="lgrated4" class="lg-rating__star" aria-label="4 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate2" id="lgrated3" value="3" checked disabled><label for="lgrated3" class="lg-rating__star" aria-label="3 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate2" id="lgrated2" value="2" disabled><label for="lgrated2" class="lg-rating__star" aria-label="2 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
              <input type="radio" name="lg-demo-rate2" id="lgrated1" value="1" disabled><label for="lgrated1" class="lg-rating__star" aria-label="1 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
            </div>
          </div>
        </div>
```

- [ ] **Step 4：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 「圖示引用 … 全部存在」(`star-fill` 已在 icons.json,新被引用;無缺圖)、`index.html` 重生。

- [ ] **Step 5：grep 確認產物**

Run: `grep -c "lg-rating__star" index.html`
Expected: ≥ 10(兩組 demo 各 5 星;CSS 內聯後更多)。

Run: `grep -c "ph-star-fill" index.html`
Expected: ≥ 10。

Run: `grep -c "lg-rating--disabled" index.html`
Expected: ≥ 2(CSS 規則 + demo)。

- [ ] **Step 6：Chromium 實機目視（使用者 gate）**

開 `index.html` → 元件展示分頁 → Rating tile,確認:
- 第一組預設左起 4 顆 accent;滑過星星 → **即時預覽**到該顆(含該顆彈一下),離開回到已選;點下 → 固定該分數。
- 改點別顆即換分;方向鍵在組內移動、聚焦的星有 ring。
- 第二組(disabled):整體淡、不可 hover/點(固定顯示 3 星)。
- 深色主題對比 OK;非 Chromium:星顯示/選取正常、無 console 錯誤。

**交使用者檢查,核可後才進 Task 2。**

- [ ] **Step 7：Commit**

```bash
git add liquid-glass.css site.src.html index.html
git commit -m "$(printf '表單家族 A:Rating .lg-rating(CSS + 展示)\n\n5 星 radio 評分,純 CSS 零 JS:reverse DOM + ~ 選擇器 hover 預覽 + 點選;\n單一 star-fill 變色(dim→accent)。星非玻璃。元件展示加一般(4★)+\ndisabled(3★)兩組。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

**Files:**
- Modify: `site.src.html`（`SNIPPETS` 加 `rating` 鍵;程式碼庫加 `<details>` 條目）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段,步進器那行之後加「星等評分」一行）

**Interfaces:**
- Consumes：Task 1 的 `.lg-rating` / `.lg-rating__star` 與 demo HTML 結構。

- [ ] **Step 1：`SNIPPETS` 加 `rating` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {` 內,緊接 `stepper:` 條目(第 1913 行)之後加入:

```javascript
  rating: '<div class="lg-rating" role="radiogroup" aria-label="評分">\n  <input type="radio" name="rate" id="r5" value="5"><label for="r5" class="lg-rating__star" aria-label="5 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>\n  <input type="radio" name="rate" id="r4" value="4" checked><label for="r4" class="lg-rating__star" aria-label="4 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>\n  <input type="radio" name="rate" id="r3" value="3"><label for="r3" class="lg-rating__star" aria-label="3 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>\n  <input type="radio" name="rate" id="r2" value="2"><label for="r2" class="lg-rating__star" aria-label="2 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>\n  <input type="radio" name="rate" id="r1" value="1"><label for="r1" class="lg-rating__star" aria-label="1 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>\n</div>',
```

- [ ] **Step 2:「元件程式碼庫」加 Rating 條目**

在 `site.src.html` 程式碼庫中,找到步進器條目 `<details class="acc lg-static lg"> … data-snippet="stepper" … </details>`(`data-snippet="stepper"` 在第 1544 行)。在其結束 `</details>` 之後插入:

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">星等評分<em>Rating</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="rating"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md`「## 元件結構」段,步進器那行(`步進器:<div class="lg lg-stepper"…`,第 128 行)之後新增:

```text
星等評分:<div class="lg-rating" role="radiogroup"><input type="radio" name="rate" id="r5" value="5"><label for="r5" class="lg-rating__star"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>…(星 5→1 倒序,共 5 組 input+label)…</div>(純 CSS 零 JS;reverse DOM + flex-direction:row-reverse 視覺正序;hover 預覽 + 點選;radio value=分數;單一 star-fill 變色 off=dim/on=accent;disabled 加 .lg-rating--disabled + 原生 disabled)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖。

Run: `grep -c "data-snippet=\"rating\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫,展開「星等評分 Rating」,確認顯示正確片段、可複製。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:Rating 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 rating、程式碼庫加 Rating 手風琴、CLAUDE.md AI 規格書\n元件結構段補星等評分一行。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**(對 `2026-06-22-form-controls-rating-design.md`):
- 結構(.lg-rating role=radiogroup / 星 5→1 倒序 / input+label.lg-rating__star / row-reverse / 隱藏 radio)→ Task 1 Step 1+3 ✓
- 四條 cascade 規則照抄(dim / checked~ / hover-reset / hover-preview)+ hover scale → Step 1 ✓
- focus-visible ring、disabled(修飾類 + pointer-events:none)、reduced-motion → Step 1+2 ✓
- 單一 star-fill currentColor、off/on token、星非玻璃、零 JS、不引入 :has()、無新圖示 → Global Constraints + Step 1 ✓
- 整合(CSS 8e / 展示 / CLAUDE.md / 程式碼庫 / build)→ Task 1 + Task 2 ✓
- YAGNI 不做半星 / 唯讀 / 尺寸 / 非 5 星 / 清除 → 未含 ✓
- 驗收清單 → Step 6 對應 ✓

**2. Placeholder scan:** 無 TBD/TODO;code step 皆完整(含完整 10 個 svg 的 demo);指令有 expected。CLAUDE.md 行用「…(共 5 組)…」省略中間三組是**刻意精簡**(完整 5 星過長,結構已由首尾 + 註解表達),非 placeholder。✓

**3. Type/name consistency:** `.lg-rating`/`__star`/`--disabled`、`data-snippet="rating"`/`SNIPPETS.rating`、demo `name="lg-demo-rate"`/`"lg-demo-rate2"`(頁面唯一、兩組不互相干擾)、id `lgrate*`/`lgrated*`、`#ph-star-fill` 各處一致;DOM 順序 input→label(相鄰 `+` focus 規則、`~` cascade)相符;倒序 5→1 + row-reverse 一致。✓
