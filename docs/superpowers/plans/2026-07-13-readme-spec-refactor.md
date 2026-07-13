# README 重構 + SPEC.md 單一真相 — 實作計畫

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增根目錄 `SPEC.md` 作為元件規格唯一真相(結構化 Markdown、26 件元件),`build_site.py` 注入展示站,README 瘦身為人類入口,其餘文件改指路。

**Architecture:** 規格書目前三副本(CLAUDE.md 最新;README 與 site.src.html **皆為舊版 18 件**——此點為計畫階段查證新發現,設計文件成文時誤判 site.src.html 為最新)。本計畫以 CLAUDE.md 的規格塊為內容基準,重寫為結構化 Markdown 存入 SPEC.md;site.src.html 的 `var SPEC = [...]` 陣列(line 2028–2077)改為 `{{AI_SPEC}}` 佔位符,build 以 `json.dumps` 轉義注入。

**Tech Stack:** Python 3(無第三方套件)、純 HTML/Markdown。無測試框架——驗證 = 跑 build + grep 斷言 + 瀏覽器人工目視。

**Spec:** `docs/superpowers/specs/2026-07-13-readme-ai-spec-refactor-design.md`

## Global Constraints

- 建置指令固定為 `python3 build_site.py`;任何對 site.src.html / SPEC.md 的修改都要重跑才反映到 index.html。
- 絕不執行 `assemble_*.py`、不引入 `partials/`(CLAUDE.md 鐵律)。
- `{{...}}` 佔位符不手動展開。
- 圖示引用必須是完整字面量(如 `#ph-trend-up`),不可字串拼接。
- 全部文件為繁體中文,沿用各檔既有標點風格(llms.txt / AGENTS.md 用全形「：」「，」;README / CLAUDE.md 用半形逗號)。
- 元件數固定口徑:**26 件**(原 18 件 + 表單家族 8 件)。
- site.src.html:1874「一連畫了十八幅」是莫內畫作說明,**不是**元件計數,不可改。
- index.html 是 build 產物且有納入版控:凡重跑 build 的 task,commit 需一併包含 index.html。

---

### Task 1: 建立分支與 SPEC.md(元件規格單一真相)

**Files:**
- Create: `SPEC.md`

**Interfaces:**
- Produces: 根目錄 `SPEC.md`(UTF-8 Markdown)。Task 2 的 build 注入、Task 3–5 的指路連結都指向此檔。開頭宣告 + 鐵則 + 26 件元件 + 屬性 + JS API + 材質 + Tokens + patterns 指路。

- [ ] **Step 1: 建立工作分支**

```bash
git checkout -b docs/spec-single-truth
```

- [ ] **Step 2: 寫入 SPEC.md 全文**

用 Write 工具建立 `SPEC.md`,內容如下(**完整照抄,這就是交付物**;內容基準 = CLAUDE.md 的「AI 規格書」塊,結構化為 Markdown、內容等價不增減):

````markdown
# Liquid Glass Kit — AI 使用規格

> **本檔是元件規格的單一真相。** 新增或修改元件時同步更新本檔;展示站「AI 整合」分頁由 `build_site.py` 自動注入本檔全文,README 與 AGENTS.md 只指路,不留副本。
> 給 AI:照本規格使用元件,不要自創玻璃樣式。本檔全文也可直接貼給對話式 AI 使用。

零依賴液態玻璃 UI 工具包(透明玻璃、即時折射、發光背景、拖曳),26 件元件。
專案內已有兩個檔案:`liquid-glass.css`、`liquid-glass.js`。

## 初始化(每頁一次)

```html
<link rel="stylesheet" href="liquid-glass.css">
<script src="liquid-glass.js"></script>
<script>LiquidGlass.init();</script>
```

## 鐵則

1. 玻璃只用於浮在內容之上的控制層(導航、卡片、面板、對話框、dock);文章、圖片等內容本身不上玻璃。
2. 折射玻璃 = `class="lg"` + `data-lg`;小型或大量重複的元件(列表項、標籤)改用 `class="lg lg-static"`(磨砂、無折射、便宜)。
3. 頁面必須有圖像或多彩背景,玻璃效果才看得見。
4. 不要手寫 `backdrop-filter` 或自製玻璃 CSS,一律使用工具包的 class 與 API。
5. 動態插入的節點呼叫 `LiquidGlass.attach(el)`;非 Chromium 瀏覽器會自動降級為磨砂,無需處理。
6. 儀表元件(統計卡/進度條/環形儀表/圖表)= 玻璃容器 + 實心內容層:數字、走勢圖、圖表本身不透明,只有外框是玻璃——內容上玻璃會看不見,這是技術上必要的邊界。

## 元件結構

### 按鈕

```html
<button class="lg lg-btn" data-lg>文字</button>
```

- 修飾:`lg-btn--pill` / `lg-btn--accent` / `lg-btn--icon` / `lg-btn--lg` / `lg-btn--sm`。

### 卡片

```html
<div class="lg lg-card" data-lg>
  <h4 class="lg-card__title">…</h4>
  <p class="lg-card__meta">…</p>
</div>
```

### 導航列

```html
<nav class="lg lg-navbar" data-lg>
  <span class="lg-navbar__brand">…</span>
  <span class="lg-navbar__spacer"></span>
  <button class="lg-navbar__link is-active">…</button>
</nav>
```

### 搜尋框

```html
<div class="lg lg-search" data-lg>
  <svg>…</svg>
  <input type="search">
  <kbd>⌘K</kbd>
</div>
```

### 文字輸入

```html
<div class="lg-field">
  <div class="lg lg-field__box" data-lg>
    <input id="f1" class="lg-field__input" placeholder=" ">
    <label for="f1" class="lg-field__label">標籤</label>
    <button type="button" class="lg-field__clear" data-lg-clear aria-label="清除"><svg viewBox="0 0 256 256"><use href="#ph-x"/></svg></button>
  </div>
  <span class="lg-field__hint">說明</span>
</div>
```

- 浮動標籤純 CSS;**placeholder 必須是一個空格 `" "`**。
- 清除鈕點擊由 `data-lg-clear` 委派處理。
- error 加 `.lg-field--error`,並對 input 加 `aria-invalid="true"` 與 `aria-describedby` 指向 hint 的 id,讓螢幕報讀器播報錯誤;disabled 加 `.lg-field--disabled`;readonly 用原生屬性。

### 多行輸入

```html
<div class="lg-field lg-field--area">
  <div class="lg lg-field__box" data-lg>
    <textarea id="t1" class="lg-field__input" placeholder=" " rows="3"></textarea>
    <label for="t1" class="lg-field__label">標籤</label>
  </div>
  <span class="lg-field__hint">說明</span>
</div>
```

- 複用 `.lg-field` 的 `--area` 修飾;`<textarea>` 換 `<input>`、label 貼頂、可垂直 resize、無清除鈕;狀態與浮動標籤同 `.lg-field`。

### 開關

```html
<label class="lg-switch">
  <input type="checkbox">
  <span class="lg-switch__track"><span class="lg-switch__thumb"></span></span>
  標籤
</label>
```

### 核取方塊

```html
<label class="lg-check">
  <input type="checkbox">
  <span class="lg-check__box"><svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg></span>
  <span class="lg-check__label">標籤</span>
</label>
```

- 純 CSS 零 JS;checked / indeterminate 填 accent;indeterminate 由 `input.indeterminate = true` 驅動;disabled 用原生屬性。

### 單選

```html
<div class="lg-radio-group" role="radiogroup">
  <label class="lg-radio">
    <input type="radio" name="g" value="a" checked>
    <span class="lg-radio__box"></span>
    <span class="lg-radio__label">標籤</span>
  </label>
  <label class="lg-radio">
    <input type="radio" name="g" value="b">
    <span class="lg-radio__box"></span>
    <span class="lg-radio__label">標籤</span>
  </label>
</div>
```

- 純 CSS 零 JS;圓 box + 中心圓點;同組共用 `name` 即單選;disabled 用原生屬性;無 indeterminate。

### 步進器

```html
<div class="lg lg-stepper" data-lg>
  <button type="button" class="lg-stepper__btn" data-lg-step="-1" aria-label="減少"><svg viewBox="0 0 256 256"><use href="#ph-minus"/></svg></button>
  <input class="lg-stepper__input" type="number" value="1" min="0" max="10" step="1">
  <button type="button" class="lg-stepper__btn" data-lg-step="1" aria-label="增加"><svg viewBox="0 0 256 256"><use href="#ph-plus"/></svg></button>
</div>
```

- 玻璃容器;值為 native number input;−/+ 由 `data-lg-step` 委派呼叫 stepUp/stepDown,native clamp 在 min/max;隱藏原生 spinner;disabled 加 `.lg-stepper--disabled` + 原生 disabled。

### 星等評分

```html
<div class="lg-rating" role="radiogroup">
  <input type="radio" name="rate" id="r5" value="5"><label for="r5" class="lg-rating__star"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
  <input type="radio" name="rate" id="r4" value="4"><label for="r4" class="lg-rating__star"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
  <!-- r3、r2、r1 依同樣式樣續排:星 5→1 倒序,共 5 組 input+label -->
</div>
```

- 純 CSS 零 JS;reverse DOM + `flex-direction: row-reverse` 視覺正序;hover 預覽 + 點選;radio value = 分數。
- 單一 `star-fill` 變色 off=dim / on=accent;disabled 加 `.lg-rating--disabled` + 原生 disabled。

### 驗證碼

```html
<div class="lg-otp" role="group">
  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" autocomplete="one-time-code">
  <!-- 共 6 格 input -->
</div>
```

- N 個磨砂 input;initOtp 自動進格 / 退格回上一格並清值 / 貼上從第一格分配。
- 值由各 `.lg-otp__cell` 串接;type 用 text 才支援 maxlength;disabled 用原生屬性。

### 檔案上傳

```html
<div class="lg lg-upload" data-lg data-lg-upload>
  <input type="file" class="lg-upload__input" multiple>
  <div class="lg-upload__prompt">
    <svg class="lg-upload__icon" viewBox="0 0 256 256"><use href="#ph-cloud-arrow-up"/></svg>
    <p class="lg-upload__title">拖放或點擊瀏覽</p>
  </div>
  <ul class="lg-upload__list"></ul>
</div>
```

- 折射玻璃拖放區;initUpload 自動接手:點擊瀏覽 / 拖放 / 清單個別移除,以 DataTransfer 回寫 `input.files`。
- input 視覺隱藏但可鍵盤聚焦;UI 控制件不做網路上傳;disabled 加 `.lg-upload--disabled` + 原生 disabled。

### 滑桿

```html
<div class="lg lg-slider" data-lg>
  <input class="lg-slider__input" type="range">
</div>
```

### 分頁

```html
<div class="lg lg-tabs" data-lg role="tablist">
  <span class="lg-tabs__pill"></span>
  <button class="lg-tabs__tab is-active" role="tab">…</button>
  …
</div>
```

### 對話框

```html
<div class="lg-modal" id="m1">
  <div class="lg-modal__overlay" data-lg-close></div>
  <div class="lg-modal__panel lg" data-lg role="dialog">…</div>
</div>
```

- 以 `<button data-lg-open="#m1">` 開啟、`data-lg-close` 關閉。
- morph:由 `<button data-lg-open>` 開啟時,對話框會從該按鈕變形長出(FLIP);ESC / `data-lg-close` 收回按鈕。reduced-motion 或無觸發按鈕時降級為液滴動畫。

### Dock

```html
<div class="lg lg-dock" data-lg>
  <button class="lg-dock__item">icon</button>
  …
</div>
```

- 自帶鄰近放大。

### 標籤與徽章

```html
<span class="lg-chip">…</span>
<span class="lg-badge">3</span>
```

### 工具提示

任何元素加 `data-lg-tip="文字"`。

### 拖曳

元素加 `data-lg-drag="viewport|parent"`(可選 `data-lg-drag-handle=".selector"`),或:

```js
LiquidGlass.draggable(el, { bounds, inertia })
```

### 統計卡

```html
<div class="lg lg-stat" data-lg>
  <span class="lg-stat__label">標籤</span>
  <div class="lg-stat__row">
    <span class="lg-stat__value" data-lg-value="48250" data-lg-prefix="$"></span>
    <span class="lg-stat__delta"><svg><use href="#ph-trend-up"/></svg>12.4%</span>
  </div>
  <svg class="lg-stat__spark" data-lg-spark="28,31,30,36,40,44"></svg>
</div>
```

- 漲綠跌紅:徽章加 `lg-stat__delta--down`。

### 進度條

```html
<div class="lg-meter" data-lg-value="68"></div>
```

- 本身非玻璃:凹槽軌道 + 實心液體填充,前緣有彎月鼓頭。

### 環形儀表

```html
<div class="lg lg-gauge" data-lg data-lg-press data-lg-profile="circle" data-lg-value="74" data-lg-unit="%" data-lg-label="Goal"></div>
```

### 圖表

```html
<div class="lg lg-chart" data-lg>
  <div class="lg-chart__head"><h4 class="lg-chart__title">標題</h4></div>
  <svg class="lg-chart__svg" data-lg-chart="line" data-lg-points="1240,1390,1180,1620" data-lg-labels="Mon,Tue,Wed,Thu"></svg>
</div>
```

- `data-lg-chart` 可為 `line` 或 `bar`;手刻 SVG、零依賴、hover 顯數值。

### 通知

```js
LiquidGlass.toast({ title, message, icon, duration })
```

- JS 呼叫;右下堆疊、自動消退、最多 4 則。

### 發光背景

```html
<div class="lg-glow" style="--lg-glow-base:#7d92ad;">
  <div class="lg-glow__image" style="--lg-bg-image:url(bg.jpg);"></div>
</div>
```

## 屬性(單一元素覆寫)

| 屬性 | 作用 |
| --- | --- |
| `data-lg-refraction` | 折射倍率,預設 1.25 |
| `data-lg-chromatic` | 色散 0–1 |
| `data-lg-blur` | 模糊 |
| `data-lg-saturate` | 飽和 |
| `data-lg-bezel` | 斜面 px |
| `data-lg-thickness` | 厚度 px |
| `data-lg-profile` | `squircle` / `circle` / `lip` |
| `data-lg-concentric` | 同心圓角:子半徑自動 = 最近 lg 父層半徑 − 內距,四角各算 |
| `data-lg-shrink` | navbar / tabs:往下捲先縮小、再隱藏(滑出上緣);往上捲現身、回頂展開;監聽 window 捲動,reduced-motion 定展開態 |
| `data-lg-scroll-edge="top|bottom|both"` | 捲動容器:內容捲到上/下緣自動漸隱;mask 直接掛容器,到頂/到底對應緣不淡 |

### 儀表資料(屬性驅動)

- `data-lg-value`(統計卡/進度條/環形儀表的目標值)、`data-lg-spark`(統計卡走勢逗號數列)、`data-lg-points` + `data-lg-labels`(圖表資料)、`data-lg-prefix` / `-suffix` / `-decimals`(數字格式)。
- 改變 `data-lg-value` / `-spark` / `-points` 即觸發彈簧動畫(單一 MutationObserver 自動接手,無需手動呼叫)。

## JS API

`LiquidGlass.init(config?)` / `attach(el, opts?)` / `draggable(el, opts?)` / `refresh()` / `toast({ title, message, icon, duration })` / `config` / `supported` / `reducedMotion`

## 材質變體

class 加 `lg--clear`(預設,較透)或 `lg--regular`(較霧,內容上用)。優先序:單元素 `data-lg-*` > 材質 class > 全域 config。

## Tokens(:root 覆寫)

`--lg-accent`(品牌色,預設 #cf6045)、`--lg-tint`、`--lg-text`、`--lg-radius-s/m/l/pill`、`--lg-blur-fallback`、`--lg-font`
主題:`<html data-lg-theme="dark">`,不設則跟隨系統。

## 進階:深色主題 / 儀表板 / 多模組介面

先讀 [docs/case-imarine.md](docs/case-imarine.md)(patterns 層:深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim),其 **§5** 是可直接接在本規格之後使用的補充規格。
````

- [ ] **Step 3: 驗證關鍵內容都在**

```bash
grep -c "lg-otp\|lg--regular\|data-lg-concentric\|data-lg-scroll-edge\|morph" SPEC.md
```

Expected: 數字 ≥ 5(表單家族、材質變體、新屬性、morph 都收錄)。再確認:

```bash
grep -n "26 件元件" SPEC.md && grep -n "單一真相" SPEC.md
```

Expected: 各至少 1 行。

- [ ] **Step 4: Commit**

```bash
git add SPEC.md
git commit -m "docs(spec-file): 新增 SPEC.md 元件規格單一真相(結構化 Markdown,26 件元件)"
```

---

### Task 2: build 注入 — site.src.html 佔位符 + build_site.py

**Files:**
- Modify: `site.src.html:2028-2077`(`var SPEC = [` 到 `].join('\n');` 整段)
- Modify: `build_site.py`
- Modify: `index.html`(build 產物,重跑後一併 commit)

**Interfaces:**
- Consumes: Task 1 的 `SPEC.md`。
- Produces: build 後 `index.html` 的 `var SPEC = "…"` 內含 SPEC.md 全文;`{{AI_SPEC}}` 佔位符機制。展示站既有的 `#specCode` 渲染與 `copyChatTemplate` 複製按鈕**不改**,自動沿用新字串。

- [ ] **Step 1: site.src.html 換佔位符(失敗測試的前半)**

把 `site.src.html` 第 2028–2077 行(從 `var SPEC = [` 到 `].join('\n');` 含兩端)整段替換為一行:

```js
var SPEC = {{AI_SPEC}};
```

注意保留上方 `/* ---------- AI 規格書 ---------- */` 註解與下方 `document.getElementById('specCode').textContent = SPEC;` 不動。

- [ ] **Step 2: 跑 build 驗證它如預期失敗**

```bash
python3 build_site.py
```

Expected: **FAIL** — 輸出 `未替換: ['{{AI_SPEC}}']` 且 exit code 1(現有 leftover 檢查抓到未注入的佔位符,證明佔位符生效)。

- [ ] **Step 3: build_site.py 加入注入邏輯**

三處修改。第一,讀檔區(現有 `icons = json.load(...)` 之後)加:

```python
spec_path = f'{KIT}/SPEC.md'
if not os.path.exists(spec_path):
    print('缺少 SPEC.md(元件規格單一真相,build 需注入展示站)'); sys.exit(1)
spec = open(spec_path, encoding='utf-8').read()
```

第二,圖示掃描改為同時掃 SPEC.md(替換現有 `refs = set(...)` 一行):

```python
refs = set(re.findall(r'#ph-([a-z0-9-]+)', tpl)) | set(re.findall(r'#ph-([a-z0-9-]+)', spec))
```

第三,在 `out = (tpl` 的替換鏈中加一行(位置放 `{{CSS}}` 之前即可),並在鏈前加佔位符存在檢查:

```python
if '{{AI_SPEC}}' not in tpl:
    print('site.src.html 缺少 {{AI_SPEC}} 佔位符'); sys.exit(1)
```

```python
       .replace('{{AI_SPEC}}', json.dumps(spec, ensure_ascii=False).replace('</', '<\\/'))
```

`json.dumps` 產生合法 JS 雙引號字串字面量(換行、引號、反斜線全轉義);`</` → `<\/` 防止規格文中的 `</script>` 提前終結 `<script>` 區塊(與原陣列手寫 `<\/script>` 同理)。

- [ ] **Step 4: 跑 build 驗證通過與注入內容**

```bash
python3 build_site.py && grep -c "單一真相" index.html && ! grep -q "{{AI_SPEC}}" index.html && echo OK
```

Expected: build 印出 `圖示引用 N 種,全部存在` 與 `index.html 完成:… KB`;`單一真相` 計數 ≥ 1(注入的是新規格);無殘留佔位符;最後印 `OK`。

- [ ] **Step 5: 負向測試 — SPEC.md 缺檔要 fail-fast**

```bash
mv SPEC.md SPEC.md.bak && python3 build_site.py; echo "exit=$?"; mv SPEC.md.bak SPEC.md
```

Expected: 印出 `缺少 SPEC.md(元件規格單一真相,build 需注入展示站)` 且 `exit=1`,檔案還原。

- [ ] **Step 6: 還原後重跑 build 並 commit**

```bash
python3 build_site.py
git add site.src.html build_site.py index.html
git commit -m "build: SPEC.md 經 {{AI_SPEC}} 注入展示站 AI 分頁(取代內嵌舊版規格陣列)"
```

- [ ] **Step 7: 瀏覽器人工確認(Chromium)**

開啟 `index.html` → 「AI 整合」分頁:規格書全文顯示為新版 Markdown(可看到「文字輸入」「材質變體」等節)、「複製」按鈕複製到完整規格 + 任務模板。此步驟為人工目視,無法自動化。

---

### Task 3: CLAUDE.md 改指路(刪內嵌規格 + 鐵律)

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `SPEC.md`(Task 1)。
- Produces: CLAUDE.md 不再內嵌規格全文;維護者(與未來的 Claude session)被引導至 SPEC.md,且鐵律要求規格只改一處。

- [ ] **Step 1: 建置流程節補 SPEC.md**

把「`build_site.py` 會把 `liquid-glass.css`、`liquid-glass.js`、`assets/` 的圖檔與 `assets/icons.json` 的圖示,全部內聯進…」該 bullet 改為:

```markdown
- `build_site.py` 會把 `liquid-glass.css`、`liquid-glass.js`、`assets/` 的圖檔、`assets/icons.json` 的圖示,以及根目錄 `SPEC.md` 的規格全文,全部內聯進 `site.src.html` 的 `{{...}}` 佔位符,輸出成自足的 `index.html`。
- 任何對 `site.src.html` / `liquid-glass.css` / `liquid-glass.js` / `assets/` / `SPEC.md` 的修改,都要重跑這行才會反映到 `index.html`。
```

- [ ] **Step 2: 鐵律 3 補佔位符、新增鐵律 6**

鐵律 3 的佔位符列表 `{{CSS}}`、`{{JS}}`、`{{ICON_SPRITE}}`、`{{IMG_*}}` 改為 `{{CSS}}`、`{{JS}}`、`{{ICON_SPRITE}}`、`{{IMG_*}}`、`{{AI_SPEC}}`。鐵律 5 之後新增:

```markdown
6. **元件規格只改 `SPEC.md` 一處**(單一真相)。新增或修改元件時同步更新 SPEC.md;展示站由 build 注入、README 與 AGENTS.md 只指路,不要在任何檔案再造規格副本。
```

- [ ] **Step 3: 檔案結構樹加 SPEC.md**

在檔案結構樹的 `├── CLAUDE.md          ← 本檔` 之後加一行:

```
├── SPEC.md            ← 元件規格單一真相(build 注入展示站,新元件先改這裡)
```

- [ ] **Step 4: 已知狀態元件數更新**

「工具包為 **v0.1**,含 18 件元件:…」bullet 改為:

```markdown
- 工具包為 **v0.1**,含 26 件元件:按鈕、圖示按鈕、卡片、開關、滑桿、分頁、搜尋框、標籤與徽章、工具提示、對話框、導航列、Dock、拖曳,表單家族八件(文字輸入 `.lg-field`、多行輸入 `.lg-field--area`、核取方塊 `.lg-check`、單選 `.lg-radio`、步進器 `.lg-stepper`、星等評分 `.lg-rating`、驗證碼 `.lg-otp`、檔案上傳 `.lg-upload`),以及儀表板五件(統計卡 `.lg-stat`、進度條 `.lg-meter`、環形儀表 `.lg-gauge`、圖表 `.lg-chart`、通知 `LiquidGlass.toast`)。
```

- [ ] **Step 5: 整節替換「AI 規格書」**

刪除「## AI 規格書(元件結構與 API 速查)」整節(含開場句與整個 ```text 圍欄區塊,直到檔尾),替換為:

```markdown
## 元件規格(單一真相:SPEC.md)

元件結構、屬性、JS API、材質與 tokens 的完整規格在根目錄 **`SPEC.md`** —— 它是唯一真相:`build_site.py` 會把它注入展示站「AI 整合」分頁,README 與 AGENTS.md 只指路。新增或修改元件時,規格只改 SPEC.md 一處。
```

- [ ] **Step 6: 驗證與 commit**

```bash
! grep -q "AI 使用規格" CLAUDE.md && grep -c "SPEC.md" CLAUDE.md && ! grep -q "18 件元件" CLAUDE.md && echo OK
```

Expected: `SPEC.md` 出現次數 ≥ 5,印 `OK`。

```bash
git add CLAUDE.md
git commit -m "docs(claude): 規格書改指路 SPEC.md + 鐵律單一真相 + 26 件元件"
```

---

### Task 4: README 重構(精簡人類入口)

**Files:**
- Modify: `README.md`(全檔重寫)

**Interfaces:**
- Consumes: `SPEC.md`(Task 1)、既有截圖 `docs/*.webp`。
- Produces: 新 README —— hero → 能做出什麼 → 快速開始 → AI 協作(指路式) → 元件一覽(26 件、五組) → 瀏覽器支援 → 授權。

- [ ] **Step 1: 以 Write 全檔重寫 README.md**

內容如下(完整照抄;「能做出什麼」「瀏覽器支援」「授權與素材」三節與現版一致,僅前言、快速開始位置、AI 節、元件一覽改變):

````markdown
# Liquid Glass Kit

> 零依賴的「液態玻璃」UI 工具包 —— 26 個現成元件、以 Snell 定律即時計算的折射與色散、發光背景、慣性拖曳。複製兩個檔案(`liquid-glass.css` + `liquid-glass.js`)就能用,不需建置工具、不需框架。**而且特別為「與 AI 協作開發」而設計**:元件規格單一真相 [SPEC.md](SPEC.md),AI agent 讀了就會用這套元件替你拼介面。

![Liquid Glass Kit hero](docs/hero.webp)

> 折射僅 Chromium 引擎(Chrome / Edge / Arc / Electron…)完整支援,其他瀏覽器**自動降級為磨砂玻璃**,版面與互動完全不變。

---

## 用這套能做出什麼

下面全部是 `index.html` 的實際畫面 —— **每一片玻璃、每一個圖表都是工具包的 class 拼出來的,沒有一行自訂玻璃 CSS**。

**內容展廳 / 作品集** — 玻璃導覽列、Dock、搜尋、篩選分頁與卡片漂浮在畫作之上:

![內容展廳](docs/gallery.webp)

**分析儀表板** — 統計卡、折線圖、環形儀表、進度條;改一個 `data-lg-value` 屬性,數字與弧線就以彈簧一起跳動:

![分析儀表板](docs/dashboard.webp)

**深色主題** — 同一套元件,`<html data-lg-theme="dark">` 一鍵換膚:

![深色主題](docs/dark-theme.webp)

**實戰案例 — 永續智能航港生態系(iMarine)** — 9 個 screen 的深色儀表板全站,從封面到六大功能頁全部用 Kit 的 class 拼出,零自訂玻璃 CSS:

![iMarine 戰情總覽](docs/case-imarine/hero-overview.webp)

> 深色 tokens、頁面節奏、模組識別色紀律、背景層與 scrim 的完整拆解,以及一份可直接貼給 AI 的「深色儀表板補充規格」,見 **[docs/case-imarine.md](docs/case-imarine.md)**。

---

## 快速開始

```html
<link rel="stylesheet" href="liquid-glass.css">
<script src="liquid-glass.js"></script>
<script>LiquidGlass.init();</script>

<!-- 玻璃材質 + 即時折射 -->
<div class="lg lg-card" data-lg>內容</div>

<!-- 輕量磨砂(不折射,適合小或大量重複的元件) -->
<span class="lg lg-static">內容</span>
```

`class="lg"` 提供材質,`data-lg` 啟用折射,通常一起用;動態插入的節點呼叫 `LiquidGlass.attach(el)`。頁面要有圖像或多彩背景,玻璃才看得見(可用 `.lg-glow` 容器)。完整的元件結構、屬性與 JS API 都在 **[SPEC.md](SPEC.md)**。

---

## 🤖 與 AI 協作開發

這套工具包**為 AI 協作而生**:元件是固定的 class 與 API,規則濃縮成單一真相 **[SPEC.md](SPEC.md)**(鐵則、26 件元件結構、屬性、JS API、材質與 tokens),AI 不必(也不該)自己手刻 `backdrop-filter`。

**AI agent(Claude Code、Cursor、Copilot 等)——推薦用法:**

把 `liquid-glass.css`、`liquid-glass.js`、`SPEC.md` 複製進你的專案(建議連 [AGENTS.md](AGENTS.md) 一起),然後直接交代任務,例如:

> 用 Liquid Glass Kit 做一個帶導覽列與三張統計卡的儀表板

agent 會自己讀 SPEC.md,用 `.lg` class 與 `LiquidGlass` API 實作,而不是自己亂寫玻璃樣式。

**對話式 AI(ChatGPT / Claude.ai 等):**

複製 [SPEC.md](SPEC.md) 全文貼進對話,後面接上你的任務描述。

**深色主題 / 儀表板 / 多模組介面:**

讓 AI 再讀 [docs/case-imarine.md](docs/case-imarine.md)(patterns 層:深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim),其 §5 是可直接接在 SPEC 之後的補充規格。

> `index.html` 的「AI 整合」分頁內也有同一份規格書的一鍵複製按鈕與各工具設定範例。

---

## 元件一覽

26 件元件,分五組。完整 HTML 結構在 [SPEC.md](SPEC.md),也能在 `index.html` 的「元件與指引」分頁即時調參、一鍵複製。

**基礎** — 按鈕 `.lg-btn`(修飾 `--pill` `--accent` `--icon` `--lg` `--sm`)、圖示按鈕 `.lg-btn--icon`、卡片 `.lg-card`。按下有彈簧擠壓回彈。

![基礎元件:按鈕、圖示按鈕、卡片](docs/components-core.webp)

**控制** — 開關 `.lg-switch`(純 CSS)、滑桿 `.lg-slider`、分頁 `.lg-tabs`(膠囊液態遷移)、搜尋框 `.lg-search`。

![控制元件:開關、滑桿、分頁、搜尋](docs/components-controls.webp)

**表單** — 文字輸入 `.lg-field`(浮動標籤)、多行輸入 `.lg-field--area`、核取方塊 `.lg-check`、單選 `.lg-radio`、步進器 `.lg-stepper`、星等評分 `.lg-rating`、驗證碼 `.lg-otp`、檔案上傳 `.lg-upload`(拖放)。

**導覽與互動** — 導覽列 `.lg-navbar`、Dock `.lg-dock`(游標鄰近放大)、拖曳 `data-lg-drag`(慣性 + 拉伸)、工具提示 `data-lg-tip`、對話框 `.lg-modal`(從觸發按鈕 morph 長出)、標籤 `.lg-chip` · 徽章 `.lg-badge`。

![導覽元件:導覽列、Dock、拖曳](docs/components-nav.webp)

**資料視覺化** — 統計卡 `.lg-stat`、進度條 `.lg-meter`、環形儀表 `.lg-gauge`、圖表 `.lg-chart`、通知 `LiquidGlass.toast()`。全部「屬性驅動」:改 `data-lg-value` / `-spark` / `-points` 即觸發彈簧動畫。

![資料元件:統計卡、進度條、環形儀表、圖表](docs/components-data.webp)

> 這幾件是「玻璃容器 + 實心內容層」:外框是玻璃,但數字、走勢圖、圖表本身不透明——內容上玻璃會看不見,這是技術上必要的邊界。

---

## 瀏覽器支援

| 環境 | 行為 |
| --- | --- |
| Chrome / Edge / Arc / Opera / Electron 等 Chromium | 完整液態折射與色散 |
| Safari / Firefox / iOS 全部瀏覽器 | 自動降級為磨砂玻璃,版面與互動完全相同 |
| 系統「降低透明度 / 減少動態」 | 自動停用折射 / 動畫 |

偵測是自動的,不需手動處理。

## 授權與素材

程式碼可自由用於個人與商業專案。圖示來自 Phosphor Icons(MIT License);畫作為 Claude Monet《向日葵花束》(1881)、《睡蓮池上的橋》(1899)與《撐陽傘的女人(面向左)》(1886),均為公有領域。
````

- [ ] **Step 2: 驗證**

```bash
! grep -q "AI 使用規格" README.md && ! grep -q "18 個現成元件\|18 件元件" README.md && grep -c "SPEC.md" README.md && echo OK
```

Expected: `SPEC.md` 次數 ≥ 5,印 `OK`。

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(readme): 重構為精簡人類入口——刪內嵌規格、AI 節指路 SPEC.md、元件一覽 26 件五組"
```

---

### Task 5: AGENTS.md、llms.txt、展示站標題計數

**Files:**
- Modify: `AGENTS.md`(全檔重寫)
- Modify: `llms.txt`(全檔重寫)
- Modify: `site.src.html:945`(元件頁標題)
- Modify: `index.html`(rebuild)

**Interfaces:**
- Consumes: `SPEC.md`(Task 1)、注入機制(Task 2)。
- Produces: agent 入口與機器索引都指向 SPEC.md;全站計數口徑 26。

- [ ] **Step 1: 重寫 AGENTS.md**

```markdown
# Liquid Glass Kit — Agent 指引

> 給「使用本 Kit 開發介面」的 AI agent。要維護本 repo（改 Kit 本體或展示站）請改讀 CLAUDE.md。

## 這是什麼

零依賴液態玻璃 UI 工具包：liquid-glass.css + liquid-glass.js 兩檔即可用，26 個現成元件。
折射僅 Chromium 完整支援，其他瀏覽器自動降級為磨砂玻璃，版面與互動不變。

## 開始之前

- 元件規格單一真相：**SPEC.md**（初始化、鐵則、26 件元件結構、屬性、JS API、材質、tokens），先讀再動手。
- 深色主題 / 儀表板 / 多模組產品需求：先讀 docs/case-imarine.md
  （實戰 patterns：深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim），
  其 §5 是可直接接在 SPEC.md 之後使用的補充規格。

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

- SPEC.md：元件規格單一真相（先讀這個）
- docs/case-imarine.md：深色儀表板實戰案例（patterns 層）
- README.md：人類入口（展示與快速開始）
- llms.txt：機器可讀索引
- CLAUDE.md：維護者專用（建置流程與鐵律）
```

- [ ] **Step 2: 重寫 llms.txt**

```markdown
# Liquid Glass Kit

> 零依賴液態玻璃 UI 工具包：26 個元件、Snell 定律即時折射、發光背景、慣性拖曳。複製 liquid-glass.css + liquid-glass.js 兩檔即可用，為 AI 協作而生。折射僅 Chromium 完整支援，其他瀏覽器自動降級磨砂。

## 核心

- [SPEC.md](SPEC.md): 元件規格單一真相（初始化、鐵則、26 件元件結構、屬性、JS API、材質、tokens）——用本 Kit 開發前必讀
- [README](README.md): 人類入口（展示、快速開始、AI 協作指引）
- [liquid-glass.css](liquid-glass.css): 工具包樣式
- [liquid-glass.js](liquid-glass.js): 工具包引擎

## 實戰 Patterns

- [iMarine 深色儀表板案例](docs/case-imarine.md): 深色 tokens、頁面節奏（supporting pane）、模組色相紀律、背景層與 scrim；§5 有可貼給 AI 的補充規格

## Optional

- [AGENTS.md](AGENTS.md): 給使用本 Kit 的 AI agent 的精簡指引
- [CLAUDE.md](CLAUDE.md): 維護本 repo 的開發規則（建置流程、鐵律）
```

- [ ] **Step 3: 展示站元件頁標題**

`site.src.html:945` 的 `<h2 class="display">十八件玻璃元件</h2>` 改為:

```html
<h2 class="display">二十六件玻璃元件</h2>
```

(注意:site.src.html:1874「一連畫了十八幅」是莫內畫作說明,不可改。)

- [ ] **Step 4: Rebuild 與驗證**

```bash
python3 build_site.py && grep -c "二十六件玻璃元件" index.html
```

Expected: build 成功,計數 = 1。

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md llms.txt site.src.html index.html
git commit -m "docs: AGENTS.md/llms.txt 指路 SPEC.md + 全站計數改 26 件"
```

---

### Task 6: 全 repo 驗證 + HANDOFF 更新

**Files:**
- Modify: `HANDOFF.md`(最後更新段)

**Interfaces:**
- Consumes: Task 1–5 全部產出。
- Produces: 驗證通過的分支,待人工瀏覽器驗收後合併。

- [ ] **Step 1: 全 repo 驗證掃描**

```bash
python3 build_site.py
grep -rn "18 個元件\|18 件元件\|18 個現成元件\|十八件玻璃元件" README.md AGENTS.md llms.txt CLAUDE.md SPEC.md site.src.html index.html; echo "stale-count exit=$?"
grep -n "{{AI_SPEC}}" index.html; echo "leftover exit=$?"
grep -c "單一真相" index.html
```

Expected: build 成功;兩個 grep 無輸出且 `exit=1`(找不到 = 通過);`單一真相` 計數 ≥ 1。
(HANDOFF.md 與 docs/superpowers/ 內的歷史敘述不在掃描範圍,保留原貌。)

- [ ] **Step 2: 更新 HANDOFF.md 最後更新段**

把 HANDOFF.md 現有「最後更新:2026-07-13(**iMarine 實戰案例收錄…**」該行的日期括號內容前面,插入本輪摘要,改為:

```markdown
最後更新:2026-07-13(**README 重構 + SPEC.md 單一真相**:新增根目錄 SPEC.md(結構化 Markdown、26 件元件)作為元件規格唯一真相,build_site.py 經 {{AI_SPEC}} 注入展示站 AI 分頁;README 瘦身為人類入口、CLAUDE.md/AGENTS.md/llms.txt 改指路、展示站標題改二十六件。spec:docs/superpowers/specs/2026-07-13-readme-ai-spec-refactor-design.md;plan:docs/superpowers/plans/2026-07-13-readme-spec-refactor.md。範圍外待辦:components-*.webp 補拍表單家族截圖。同日稍早的 iMarine 案例收錄見下段。)
```

原 iMarine 那句話的內容移到緊接其後的獨立引文行或併入其段落開頭(保留原文字,不刪資訊)。

- [ ] **Step 3: Commit**

```bash
git add HANDOFF.md
git commit -m "docs(handoff): README 重構 + SPEC.md 單一真相收尾記錄"
```

- [ ] **Step 4: 人工驗收提醒(合併前)**

以 Chromium 開 `index.html` 確認:AI 整合分頁規格全文與複製按鈕、元件頁標題「二十六件玻璃元件」。README 在 GitHub 預覽確認圖片與連結(SPEC.md、AGENTS.md、docs/case-imarine.md)可點。通過後依 finishing-a-development-branch 流程合併回 main。

---

## Self-Review 紀錄

- Spec 覆蓋:§1 架構(Task 1+2)、§2 SPEC.md 內容(Task 1)、§3 README(Task 4)、§4 周邊檔案(Task 3/5)、驗證(各 task Step + Task 6)、錯誤處理(Task 2 Step 3/5:缺檔 fail、佔位符缺失 fail、leftover 檢查)。範圍外(截圖、選型指引、AI 分頁 UI)未混入。
- 設計文件兩個「實作時查證」技術點已在計畫階段查證完畢:注入格式 = `json.dumps` + `</` 轉義;圖示掃描 = 掃 tpl 原始檔,故補掃 SPEC.md(Task 2 Step 3)。
- 額外發現並納入:site.src.html 的 SPEC 陣列也是舊版(非設計文件所稱最新)、site.src.html:945 標題計數、CLAUDE.md 已知狀態計數。
- 型別/名稱一致性:佔位符統一 `{{AI_SPEC}}`;分支名 `docs/spec-single-truth`;SPEC.md 標題「Liquid Glass Kit — AI 使用規格」與展示站分頁語境一致。
