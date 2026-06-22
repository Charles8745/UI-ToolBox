# Textarea（`.lg-field--area`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增多行輸入 `.lg-field--area`,複用 Text field 的 `.lg-field` 殼,家族 A 第三件。

**Architecture:** 複用既有 `.lg-field` / `.lg-field__box` / 浮動標籤 / 狀態 / token(DRY),只加修飾類 `.lg-field--area`(兩條 CSS 規則)把 `<input>` 換成 `<textarea>`:label 改貼頂、textarea 可垂直 resize、無清除鈕。**零新 JS、零新圖示**。

**Tech Stack:** `liquid-glass.css`、`site.src.html`、`CLAUDE.md`、`python3 build_site.py`。**無單元測試框架**:驗證 = build(圖示完整性 + 重生)+ grep + Chromium 目視(使用者 gate)。

## Global Constraints

- 複用 Text field,**不重做**狀態/ring/error/disabled/readonly/浮動標籤/reduced-motion;本件只加 `.lg-field--area` 兩條規則 + demo + docs。
- **陰影紀律(沿用)**:`.lg-field__box` 不重設 box-shadow / 不重畫 inset stroke(由 `.lg` + `.lg::before` 提供);ring 由既有 `:focus-within` / error 規則負責——本件**不碰** box-shadow。
- `placeholder` 必須是一個空格 `" "`(floating 機制);`<textarea>` 掛 `.lg-field__input` 以繼承樣式與相鄰 `+` 浮動規則。
- label 上浮 transform **複用** Text field 既有規則 `translateY(-16px) scale(.78)`;`--area` 只改 label 靜止位置(`align-items:flex-start; padding-top; transform-origin:left top`)。
- 不引入 `:has()`;不新增圖示;不硬編顏色/圓角(用既有 token)。
- 改完 `python3 build_site.py` 重生 `index.html`;非 Chromium 磨砂降級、resize/floating 純 DOM 不報錯。
- 既有 base 值(供對位):`.lg-field__input { padding:24px 0 6px }`、`.lg-field__label { top:0; height:100%; align-items:center; transform-origin:left center }`。`--area` 以較高特異度(0,2,0 > base 0,1,0)覆寫 input 的 padding/min-height/resize 與 label 的 top/height/transform-origin。`*{box-sizing:border-box}` 全域生效(textarea min-height 含 padding)。

---

## Task 1：`.lg-field--area` CSS + 展示 demo（使用者目視 gate）

**Files:**
- Modify: `liquid-glass.css`(第 7b 節 `.lg-field` 規則尾端,`​.lg-field__input:read-only { … }`(第 424 行)之後、`/* 8. 開關 */`(第 427 行)之前,追加 `--area` 規則)
- Modify: `site.src.html`(元件展示 Text field tile 結束 `</div>`(第 1117 行)之後插入 Textarea tile)

**Interfaces:**
- Consumes:既有 `.lg-field` / `.lg-field__box` / `.lg-field__input` / `.lg-field__label` / `.lg-field__hint` 與浮動標籤規則。
- Produces:修飾類 `.lg-field--area`(供 Task 2 與使用者引用)。

- [ ] **Step 1：在 `liquid-glass.css` 追加 `--area` 規則**

在 `.lg-field__input:read-only { color: var(--lg-text-dim); }`(第 424 行)之後、`/* ===== 8. 開關 ===== */` 註解之前,插入:

```css
/* Textarea 變體:多行,複用 __box + 浮動標籤;label 貼頂、可垂直 resize、無清除鈕 */
.lg-field--area .lg-field__input {
  resize: vertical;
  min-height: 96px;
  padding: 22px 0 10px;
  line-height: 1.45;
}
.lg-field--area .lg-field__label {
  top: 22px;
  height: auto;
  transform-origin: left top;
}
```

> 說明:label 靜止改 `top:22px; height:auto`(覆寫 base 的 `top:0; height:100%`)——讓 label 只有文字高度、不含 box 全高,落在 textarea 首行(textarea `padding-top:22px` 對齊)。**關鍵**:用 `top` 定位而非在 `height:100%` 元素上加 padding,否則 `scale(.78)` 會連同整個全高元素一起縮放、浮動位置變得依賴框高且隨 resize 漂移。上浮沿用既有 `translateY(-16px) scale(.78)` + `transform-origin:left top`(從首行 22px 縮到框上緣約 6px,與框高無關)。確切 px 於 Chromium 微調。**不新增任何 box-shadow / reduced-motion 規則**(沿用 Text field)。

- [ ] **Step 2：在 `site.src.html` 元件展示加 Textarea tile**

找到 Text field tile(`<h3>Text field</h3>`,約 1091–1117 行)的結束 `</div>`(第 1117 行)。在其之後插入:

```html
        <div class="tile lg-static lg t2">
          <div class="tile__head"><h3>Textarea</h3></div>
          <div class="tile__stage tile__stage--col" style="align-items:stretch;gap:14px;">
            <div class="lg-field lg-field--area">
              <div class="lg lg-field__box" data-lg>
                <textarea id="ta-msg" class="lg-field__input" placeholder=" " rows="3"></textarea>
                <label for="ta-msg" class="lg-field__label">訊息內容</label>
              </div>
              <span class="lg-field__hint">右下角可拖拉變高</span>
            </div>
            <div class="lg-field lg-field--area">
              <div class="lg lg-field__box" data-lg>
                <textarea id="ta-note" class="lg-field__input" placeholder=" " rows="2">莫內的睡蓮系列約 250 幅,描繪吉維尼花園的水景與光線。</textarea>
                <label for="ta-note" class="lg-field__label">備註</label>
              </div>
            </div>
          </div>
        </div>
```

- [ ] **Step 3：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 「圖示引用 … 全部存在」(不需新圖示)、`index.html` 重生。

- [ ] **Step 4：grep 確認產物**

Run: `grep -c "lg-field--area" index.html`
Expected: ≥ 4(CSS 兩條 + demo 兩個 wrapper;內聯後更多)。

Run: `grep -c "<textarea" index.html`
Expected: ≥ 2。

- [ ] **Step 5：Chromium 實機目視（使用者 gate）**

開 `index.html` → 元件展示分頁 → Textarea tile,確認:
- 「訊息內容」空欄:label 貼**首行**位置如 placeholder;點擊聚焦 → label **平滑上浮到框上緣**、轉 accent、框顯 accent ring;打多行字正常換行。
- 「備註」有值:label 維持上浮;多行內容顯示;**右下角可垂直拖拉變高**,label 不隨之移動。
- 折射顯影;深色主題對比 OK;非 Chromium / 關折射:磨砂降級、floating + resize 正常、無 console 錯誤。

**交使用者檢查,核可後才進 Task 2。**

- [ ] **Step 6：Commit**

```bash
git add liquid-glass.css site.src.html index.html
git commit -m "$(printf '表單家族 A:Textarea .lg-field--area(CSS + 展示)\n\n複用 .lg-field 殼,--area 修飾:textarea 換 input、label 貼頂\n(flex-start+padding-top+origin:left top,上浮 transform 複用)、\nresize:vertical + min-height,無清除鈕。元件展示加空態+有值態 demo。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

**Files:**
- Modify: `site.src.html`（`SNIPPETS` 加 `textarea` 鍵;程式碼庫加 `<details>` 條目）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段,文字輸入那行之後加「多行輸入」一行）

**Interfaces:**
- Consumes：Task 1 的 `.lg-field--area`、demo HTML 結構。

- [ ] **Step 1：`SNIPPETS` 加 `textarea` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {` 內,緊接 `field:` 條目(約第 1839 行)之後加入:

```javascript
  textarea: '<div class="lg-field lg-field--area">\n  <div class="lg lg-field__box" data-lg>\n    <textarea id="t1" class="lg-field__input" placeholder=" " rows="3"></textarea>\n    <label for="t1" class="lg-field__label">訊息內容</label>\n  </div>\n  <span class="lg-field__hint">最多 500 字</span>\n</div>',
```

- [ ] **Step 2:「元件程式碼庫」加 Textarea 條目**

在 `site.src.html` 程式碼庫中,找到文字輸入條目 `<details class="acc lg-static lg"> … data-snippet="field" … </details>`(約第 1483–1486 行,`data-snippet="field"` 在第 1485 行)。在其結束 `</details>` 之後插入:

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">多行輸入<em>Textarea</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="textarea"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md`「## 元件結構」段,文字輸入那行(`文字輸入:<div class="lg-field">…`,第 123 行)之後新增:

```text
多行輸入:<div class="lg-field lg-field--area"><div class="lg lg-field__box" data-lg><textarea id="t1" class="lg-field__input" placeholder=" " rows="3"></textarea><label for="t1" class="lg-field__label">標籤</label></div><span class="lg-field__hint">說明</span></div>(複用 .lg-field 的 --area 修飾;<textarea> 換 <input>、label 貼頂、可垂直 resize、無清除鈕;狀態與浮動標籤同 .lg-field)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖。

Run: `grep -c "data-snippet=\"textarea\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫,展開「多行輸入 Textarea」,確認顯示正確片段、可複製。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:Textarea 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 textarea、程式碼庫加 Textarea 手風琴、CLAUDE.md AI 規格書\n元件結構段補多行輸入一行。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**(對 `2026-06-22-form-controls-textarea-design.md`):
- 複用 `.lg-field` 殼 + `--area` 修飾、`<textarea>` 掛 `.lg-field__input` → Task 1 Step 1+2 ✓
- label 貼頂(`flex-start`+`padding-top:22px`+`origin:left top`)、上浮 transform 複用 → Step 1 ✓
- `resize:vertical` + `min-height` + textarea 內距 → Step 1 ✓
- 無清除鈕、無新 JS、無新圖示 → 計畫未含 JS/icon ✓
- 沿用狀態/陰影紀律/reduced-motion(不重做)→ Global Constraints + Step 1 說明 ✓
- demo 空態 + 有值多行態 → Step 2 ✓
- 文件(SNIPPETS / 程式碼庫 / CLAUDE.md)→ Task 2 ✓
- YAGNI 不做計數器/auto-grow/鎖死 resize → 未含 ✓
- 驗收清單 → Step 5 對應 ✓

**2. Placeholder scan:** 無 TBD/TODO;code step 皆完整;指令有 expected。✓

**3. Type/name consistency:** `.lg-field--area`、`data-snippet="textarea"`/`SNIPPETS.textarea`、`.lg-field__input`/`__label`/`__hint`、id `ta-msg`/`ta-note`/`t1` 各處一致;`--area` override 特異度(0,2,0)> base(0,1,0)勝出。

**self-review 修正(已套用):** 原本 `--area` label 用 `align-items:flex-start; padding-top:22px` 加在 base 的 `height:100%` 元素上——`scale(.78)` 會連同整個全高 label 一起縮放,浮動位置依賴框高、且 textarea resize 變高時 label 會漂移。改為 `top:22px; height:auto`(label 僅文字高度),浮動位置與框高無關、resize 不漂移。spec 同步。
**float 規則複用驗證:** base float 規則只設 `transform`+`color`,不設 `transform-origin`;故各變體保留自己的 origin(input=base `left center`、area=override `left top`),同一條 float 規則對兩者皆正確。`*{box-sizing:border-box}` 全域,textarea `min-height:96px` 含 padding。✓
