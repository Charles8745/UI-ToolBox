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
| `data-lg-scroll-edge` | 值 `top` / `bottom` / `both`;捲動容器:內容捲到上/下緣自動漸隱;mask 直接掛容器,到頂/到底對應緣不淡 |

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
