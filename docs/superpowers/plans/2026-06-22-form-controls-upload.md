# File upload（`.lg-upload`）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 為 Liquid Glass Kit 新增拖放上傳 `.lg-upload`,家族 A 第八件(#11,A 家族最後一件)。

**Architecture:** 折射玻璃面板(`lg + data-lg`)做拖放區;`initUpload(panel)` per-container 以 `DataTransfer` 為單一真實來源,處理點擊瀏覽 / 拖放 / 清單個別移除 / 回寫 `input.files`。新增 `cloud-arrow-up` 圖示。input 視覺隱藏但可鍵盤聚焦 + `:focus-within` ring。**UI 控制件,不做網路上傳。**

**Tech Stack:** `assets/icons.json`、`liquid-glass.css`、`liquid-glass.js`、`site.src.html`、`CLAUDE.md`、`python3 build_site.py`。**無單元測試框架**:驗證 = build(圖示完整性 + 重生)+ grep + Chromium 目視(使用者 gate)。

## Global Constraints

- 玻璃只做面板;檔名/大小/圖示是實心內容層。面板 `lg + data-lg`(折射)。
- **陰影紀律(同 field/stepper)**:`.lg-upload` 是 `.lg`,已有 `box-shadow:var(--lg-shadow)`——**不重設 base box-shadow**;只覆寫 `border-radius` 為 `var(--lg-radius-l)`。dragover/focus ring **必須** `box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent)`(保留基底)。
- **必須先加圖示再 build**:`assets/icons.json` 加 `cloud-arrow-up`(下方 path),否則 demo 的 `#ph-cloud-arrow-up` 引用會讓 build「缺圖」失敗。引用用完整字面量;列用既有 `#ph-file-text`、`#ph-x`。
- input **不用 `hidden`**(要可鍵盤聚焦):`.lg-upload__input { position:absolute; opacity:0; width:1px; height:1px }`;`.lg-upload:focus-within` 顯 ring。
- JS `initUpload(panel)`:`store=new DataTransfer()` 為真實來源;點擊面板(非清單區)→ `input.click()`;dragenter/over → `is-dragover`,dragleave/drop → 移除;drop/change → 去重(name+size)後 `store.items.add`、`input.files=store.files`、render;移除鈕 → `store.items.remove(i)`、回寫、render。在 `boot()` 用 `[].forEach.call(document.querySelectorAll('[data-lg-upload]'), initUpload)` 註冊。
- token 不硬編:`--lg-radius-l`、`--lg-radius-s`、`--lg-shadow`、`--lg-accent`、`--lg-tint`、`--lg-text`、`--lg-text-dim`、`--lg-font`、`--lg-speed`、`--lg-ease-out`。
- 改完 `python3 build_site.py` 重生 `index.html`;非 Chromium:點擊瀏覽 + 清單正常(拖放 API 缺則不動但不報錯)。

---

## Task 1：圖示 + `.lg-upload` CSS + `initUpload()` JS + 展示 demo（使用者目視 gate）

**Files:**
- Modify: `assets/icons.json`(第 19 行 `"circle-half"` 之後加 `"cloud-arrow-up"`)
- Modify: `liquid-glass.css`(第 8f 節 `.lg-otp`(`.lg-otp__cell:disabled`,第 727 行)之後、`/* 9. 滑桿 */`(第 730 行)之前插入「8g. 檔案上傳」節;reduced-motion 區第 1266 行 `.lg-otp__cell` 那行之後補一行)
- Modify: `liquid-glass.js`(`initOtp()` 函式結束 `}`(第 845 行)之後、`function initTooltips()` 之前插入 `initUpload()`;`boot()` 內 `[].forEach.call(document.querySelectorAll('.lg-otp'), initOtp);` 那行之後加一行 per-container 註冊)
- Modify: `site.src.html`(元件展示 OTP tile 結束 `</div>`(第 1175 行)之後插入 Upload tile)

**Interfaces:**
- Produces:class `.lg-upload` / `.lg-upload__input` / `.lg-upload__prompt` / `.lg-upload__icon` / `.lg-upload__title` / `.lg-upload__hint` / `.lg-upload__list` / `.lg-upload__file` / `.lg-upload__fileicon` / `.lg-upload__name` / `.lg-upload__size` / `.lg-upload__remove`、修飾類 `.lg-upload--disabled`、屬性 `data-lg-upload`、JS 函式 `initUpload(panel)`、圖示 `cloud-arrow-up`。

- [ ] **Step 1：在 `assets/icons.json` 加 `cloud-arrow-up` 圖示**

在第 19 行 `"circle-half": "…",` 之後新增一行(注意結尾逗號,保持 JSON 合法):

```json
"cloud-arrow-up": "M178.34,165.66,160,147.31V208a8,8,0,0,1-16,0V147.31l-18.34,18.35a8,8,0,0,1-11.32-11.32l32-32a8,8,0,0,1,11.32,0l32,32a8,8,0,0,1-11.32,11.32ZM160,40A88.08,88.08,0,0,0,81.29,88.68,64,64,0,1,0,72,216h40a8,8,0,0,0,0-16H72a48,48,0,0,1,0-96c1.1,0,2.2,0,3.29.12A88,88,0,0,0,72,128a8,8,0,0,0,16,0,72,72,0,1,1,100.8,66,8,8,0,0,0,3.2,15.34,7.9,7.9,0,0,0,3.2-.68A88,88,0,0,0,160,40Z",
```

- [ ] **Step 2：在 `liquid-glass.css` 插入 `.lg-upload` 樣式**

在 `.lg-otp__cell:disabled { opacity: 0.5; cursor: not-allowed; }`(第 727 行)之後、`/* ===== 9. 滑桿 ===== */` 註解之前,插入:

```css
/* ==================================================================== *
 * 8g. 檔案上傳  .lg-upload(折射玻璃拖放區 + DataTransfer 清單)
 * ==================================================================== */
.lg-upload {
  display: block;
  border-radius: var(--lg-radius-l);
  padding: 28px 24px;
  text-align: center;
  cursor: pointer;
  transition: box-shadow var(--lg-speed) var(--lg-ease-out);
}
.lg-upload__input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.lg-upload__prompt { display: flex; flex-direction: column; align-items: center; gap: 6px; pointer-events: none; }
.lg-upload__icon { width: 40px; height: 40px; fill: currentColor; color: var(--lg-text-dim); }
.lg-upload__title { margin: 0; font: 500 14px/1.4 var(--lg-font); color: var(--lg-text); }
.lg-upload__title strong { color: var(--lg-accent); font-weight: 600; }
.lg-upload__hint { margin: 0; font: 400 12px/1 var(--lg-font); color: var(--lg-text-dim); }
.lg-upload:focus-within,
.lg-upload.is-dragover { box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent); }
.lg-upload.is-dragover .lg-upload__icon { color: var(--lg-accent); }
.lg-upload__list { list-style: none; margin: 14px 0 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.lg-upload__list:empty { display: none; }
.lg-upload__file {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; border-radius: var(--lg-radius-s);
  background: var(--lg-tint); text-align: left;
}
.lg-upload__fileicon { width: 18px; height: 18px; flex: none; fill: currentColor; color: var(--lg-text-dim); }
.lg-upload__name { flex: 1; min-width: 0; font: 500 13px/1.2 var(--lg-font); color: var(--lg-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lg-upload__size { flex: none; font: 400 12px/1 var(--lg-font); color: var(--lg-text-dim); }
.lg-upload__remove {
  flex: none; width: 24px; height: 24px; display: grid; place-items: center;
  border: 0; border-radius: 50%; background: transparent; color: var(--lg-text-dim); cursor: pointer;
  transition: color var(--lg-speed) var(--lg-ease-out), background var(--lg-speed) var(--lg-ease-out);
}
.lg-upload__remove svg { width: 14px; height: 14px; fill: currentColor; }
.lg-upload__remove:hover { background: var(--lg-tint); color: var(--lg-text); }
.lg-upload--disabled { opacity: 0.5; pointer-events: none; }
```

> 說明:`.lg-upload` 是 `.lg`,border-radius 由 `.lg` 給 radius-m → 覆寫為 radius-l;**不設 base box-shadow**(沿用 `.lg` 的 `var(--lg-shadow)`);ring 保留 `var(--lg-shadow)`。`__prompt` 設 `pointer-events:none` 讓點擊落在面板觸發瀏覽;`__list` 不設(移除鈕可點)。

- [ ] **Step 3：在 reduced-motion 區補一行**

在 `liquid-glass.css` 第 1266 行 `.lg-otp__cell { transition-duration: 0.01s !important; }` 之後新增:

```css
  .lg-upload { transition-duration: 0.01s !important; }
```

- [ ] **Step 4：在 `liquid-glass.js` 加 `initUpload()`**

(a) 在 `initOtp()` 函式結束的 `}`(第 845 行)之後、`function initTooltips()` 之前,插入:

```javascript
  function initUpload(panel) {
    var input = panel.querySelector('.lg-upload__input');
    var list = panel.querySelector('.lg-upload__list');
    if (!input || !list) return;
    var store = new DataTransfer();
    function fmt(b) {
      if (b < 1024) return b + ' B';
      if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
      return (b / 1048576).toFixed(1) + ' MB';
    }
    function render() {
      list.innerHTML = '';
      [].forEach.call(store.files, function (file, i) {
        var li = document.createElement('li');
        li.className = 'lg-upload__file';
        li.innerHTML = '<svg class="lg-upload__fileicon" viewBox="0 0 256 256"><use href="#ph-file-text"/></svg>'
          + '<span class="lg-upload__name"></span>'
          + '<span class="lg-upload__size"></span>'
          + '<button type="button" class="lg-upload__remove" aria-label="移除"><svg viewBox="0 0 256 256"><use href="#ph-x"/></svg></button>';
        li.querySelector('.lg-upload__name').textContent = file.name;
        li.querySelector('.lg-upload__size').textContent = fmt(file.size);
        li.querySelector('.lg-upload__remove').addEventListener('click', function (e) {
          e.stopPropagation();
          store.items.remove(i);
          input.files = store.files;
          render();
        });
        list.appendChild(li);
      });
    }
    function add(files) {
      [].forEach.call(files, function (f) {
        var dup = [].some.call(store.files, function (g) { return g.name === f.name && g.size === f.size; });
        if (!dup) store.items.add(f);
      });
      input.files = store.files;
      render();
    }
    panel.addEventListener('click', function (e) {
      if (e.target.closest('.lg-upload__list')) return;
      input.click();
    });
    input.addEventListener('change', function () { add(input.files); });
    ['dragenter', 'dragover'].forEach(function (ev) {
      panel.addEventListener(ev, function (e) { e.preventDefault(); panel.classList.add('is-dragover'); });
    });
    panel.addEventListener('dragleave', function (e) { e.preventDefault(); panel.classList.remove('is-dragover'); });
    panel.addEventListener('drop', function (e) {
      e.preventDefault();
      panel.classList.remove('is-dragover');
      if (e.dataTransfer) add(e.dataTransfer.files);
    });
  }
```

(b) 在 `boot()` 內 `[].forEach.call(document.querySelectorAll('.lg-otp'), initOtp);` 那行之後加一行:

```javascript
      [].forEach.call(document.querySelectorAll('[data-lg-upload]'), initUpload);
```

- [ ] **Step 5：在 `site.src.html` 元件展示加 Upload tile**

找到 OTP tile(`<h3>OTP</h3>`)的結束 `</div>`(第 1175 行)。在其之後插入:

```html
        <div class="tile lg-static lg t3">
          <div class="tile__head"><h3>File upload</h3></div>
          <div class="tile__stage tile__stage--col" style="gap:14px;align-items:stretch;">
            <div class="lg lg-upload" data-lg data-lg-upload>
              <input type="file" class="lg-upload__input" multiple aria-label="選擇檔案">
              <div class="lg-upload__prompt">
                <svg class="lg-upload__icon" viewBox="0 0 256 256"><use href="#ph-cloud-arrow-up"/></svg>
                <p class="lg-upload__title">拖放檔案到這裡,或 <strong>點擊瀏覽</strong></p>
                <p class="lg-upload__hint">支援多檔</p>
              </div>
              <ul class="lg-upload__list"></ul>
            </div>
            <div class="lg lg-upload lg-upload--disabled" data-lg data-lg-upload>
              <input type="file" class="lg-upload__input" multiple disabled aria-label="選擇檔案">
              <div class="lg-upload__prompt">
                <svg class="lg-upload__icon" viewBox="0 0 256 256"><use href="#ph-cloud-arrow-up"/></svg>
                <p class="lg-upload__title">已停用</p>
                <p class="lg-upload__hint">disabled 狀態</p>
              </div>
              <ul class="lg-upload__list"></ul>
            </div>
          </div>
        </div>
```

- [ ] **Step 6：重建並驗證 build 通過**

Run: `python3 build_site.py`
Expected: 「圖示引用 … 全部存在」(含新加的 `cloud-arrow-up`;若缺會列出並失敗)、`index.html` 重生。

- [ ] **Step 7：grep 確認產物**

Run: `grep -c "lg-upload" index.html`
Expected: ≥ 4(兩面板 + CSS;內聯後更多)。

Run: `grep -c "initUpload" index.html`
Expected: ≥ 2(函式定義 + boot 呼叫)。

Run: `grep -c "ph-cloud-arrow-up" index.html`
Expected: ≥ 2(sprite symbol + demo 引用)。

- [ ] **Step 8：Chromium 實機目視（使用者 gate）**

開 `index.html` → 元件展示分頁 → File upload tile,確認:
- **雲朵上傳圖示**顯示正確(非破圖)。
- 點面板 → 開檔案對話框;選檔 → 清單顯示檔名 + 大小;再選/拖檔進來 → 合併、去重;點某列 `x` → 移除該檔。
- 拖檔案到面板上方 → accent ring + 圖示轉 accent;放開後加入。
- 鍵盤 Tab 到面板 → focus ring;Space/Enter 開對話框。
- 折射顯影;disabled 面板半透明、不可互動;深色對比 OK。
- 非 Chromium:磨砂降級、點擊瀏覽 + 清單正常、無 console 錯誤。

**交使用者檢查,核可後才進 Task 2。**

- [ ] **Step 9：Commit**

```bash
git add assets/icons.json liquid-glass.css liquid-glass.js site.src.html index.html
git commit -m "$(printf '表單家族 A:File upload .lg-upload(圖示 + CSS + JS + 展示)\n\n折射玻璃拖放區 + 點擊瀏覽 + DataTransfer 檔案清單(合併/去重/個別移除/\n回寫 input.files)。新增 cloud-arrow-up 圖示。input 視覺隱藏但可鍵盤聚焦 +\nfocus ring。dragover ring 保留 .lg 基底陰影。元件展示加一般 + disabled。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Task 2：文件同步（AI 規格書 + 程式碼庫 + CLAUDE.md）

**Files:**
- Modify: `site.src.html`（`SNIPPETS` 加 `upload` 鍵;程式碼庫加 `<details>` 條目）
- Modify: `CLAUDE.md`（AI 規格書「元件結構」段,驗證碼那行之後加「檔案上傳」一行）

**Interfaces:**
- Consumes：Task 1 的 `.lg-upload` 結構、`data-lg-upload`、`#ph-cloud-arrow-up`。

- [ ] **Step 1：`SNIPPETS` 加 `upload` 鍵**

在 `site.src.html` 的 `var SNIPPETS = {` 內,緊接 `otp:` 條目(第 1965 行)之後加入:

```javascript
  upload: '<div class="lg lg-upload" data-lg data-lg-upload>\n  <input type="file" class="lg-upload__input" multiple aria-label="選擇檔案">\n  <div class="lg-upload__prompt">\n    <svg class="lg-upload__icon" viewBox="0 0 256 256"><use href="#ph-cloud-arrow-up"/></svg>\n    <p class="lg-upload__title">拖放檔案到這裡,或 <strong>點擊瀏覽</strong></p>\n    <p class="lg-upload__hint">支援多檔</p>\n  </div>\n  <ul class="lg-upload__list"></ul>\n</div>',
```

- [ ] **Step 2:「元件程式碼庫」加 File upload 條目**

在 `site.src.html` 程式碼庫中,找到驗證碼條目 `<details class="acc lg-static lg"> … data-snippet="otp" … </details>`(`data-snippet="otp"` 在第 1594 行)。在其結束 `</details>` 之後插入:

```html
        <details class="acc lg-static lg">
          <summary><span class="acc__name">檔案上傳<em>File upload</em></span><svg class="ph acc__caret" width="16" height="16"><use href="#ph-caret-down"/></svg></summary>
          <div class="code"><button class="copy" data-copy><svg class="ph" width="14" height="14"><use href="#ph-copy"/></svg>複製</button><pre><code data-snippet="upload"></code></pre></div>
        </details>
```

- [ ] **Step 3:`CLAUDE.md` AI 規格書補一行**

在 `CLAUDE.md`「## 元件結構」段,驗證碼那行(`驗證碼:<div class="lg-otp"…`,第 130 行)之後新增:

```text
檔案上傳:<div class="lg lg-upload" data-lg data-lg-upload><input type="file" class="lg-upload__input" multiple><div class="lg-upload__prompt"><svg class="lg-upload__icon" viewBox="0 0 256 256"><use href="#ph-cloud-arrow-up"/></svg><p class="lg-upload__title">拖放或點擊瀏覽</p></div><ul class="lg-upload__list"></ul></div>(折射玻璃拖放區;initUpload 自動接手:點擊瀏覽 / 拖放 / 清單個別移除,以 DataTransfer 回寫 input.files;input 視覺隱藏但可鍵盤聚焦;UI 控制件不做網路上傳;disabled 加 .lg-upload--disabled + 原生 disabled)
```

- [ ] **Step 4：重建並驗證**

Run: `python3 build_site.py`
Expected: 正常重生、無缺圖。

Run: `grep -c "data-snippet=\"upload\"" index.html`
Expected: ≥ 1。

- [ ] **Step 5：Chromium 目視（程式碼庫）**

開 `index.html` → AI Guide 分頁 → 程式碼庫,展開「檔案上傳 File upload」,確認顯示正確片段、可複製。

- [ ] **Step 6：Commit**

```bash
git add site.src.html CLAUDE.md index.html
git commit -m "$(printf '表單家族 A:File upload 文件同步(AI 規格 + 程式碼庫 + CLAUDE.md)\n\nSNIPPETS 加 upload、程式碼庫加 File upload 手風琴、CLAUDE.md AI 規格書\n元件結構段補檔案上傳一行。\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

## Self-Review

**1. Spec coverage**(對 `2026-06-22-form-controls-upload-design.md`):
- 新圖示 `cloud-arrow-up` 先加 icons.json → Task 1 Step 1 ✓
- 結構(lg lg-upload data-lg data-lg-upload / 視覺隱藏可聚焦 input / prompt+icon+title+hint / list)→ Step 2+5 ✓
- initUpload(DataTransfer 來源、點擊瀏覽防清單區、drag 高亮、drop/change 去重 add、移除鈕、render+fmt)+ boot per-container 註冊 → Step 4 ✓
- dragover/focus ring 保留 `.lg` 基底陰影、不重設 base box-shadow、border-radius 覆寫 radius-l → Step 2 ✓
- disabled 修飾類 + 原生、reduced-motion、token 不硬編、列用 file-text/x → Step 2+3 ✓
- UI only 不做網路上傳 → 計畫未含 fetch/progress ✓
- 整合(icon / CSS / JS / 展示 / CLAUDE.md / 程式碼庫 / build)→ Task 1 + Task 2 ✓
- YAGNI 不做進度/驗證/縮圖/單檔模式/排序 → 未含 ✓
- 驗收清單 → Step 8 對應 ✓

**2. Placeholder scan:** 無 TBD/TODO;code step 皆完整;指令有 expected;**圖示先於 build**(Step 1 在 Step 6 前,避免缺圖失敗)。✓

**3. Type/name consistency:** `.lg-upload*` 全系列、`data-lg-upload`、`initUpload`、`data-snippet="upload"`/`SNIPPETS.upload`、`cloud-arrow-up`/`#ph-cloud-arrow-up`、`#ph-file-text`/`#ph-x` 各處一致;initUpload 取 `.lg-upload__input`/`__list` 與 demo 結構相符;boot per-container 同 `initOtp` 範式;ring 保留 `var(--lg-shadow)`(同 field/stepper)。✓
