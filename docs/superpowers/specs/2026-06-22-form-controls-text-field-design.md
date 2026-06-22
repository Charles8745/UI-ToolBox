# 表單控制家族 A — Text field 設計 spec

> 對象:Liquid Glass Kit v0.1,家族 A 第二件(接續 Checkbox)。
> 家族共同決策見 `2026-06-21-form-controls-checkbox-design.md` 的「家族 A 共同決策」段(玻璃只做控制層、宣告式 API、token、降級、reduced-motion、每件完成步驟)——此處不重複,僅補本件特有部分。
> 節奏:做完 build + Chromium 自驗 → 交使用者 Chromium 目視 → 核可。本件留在 `feat/form-family-a`,與 A 家族其餘元件一起合。
> 日期:2026-06-22。

## Text field · `.lg-field`(浮動標籤版)

**定位:** 單行文字輸入,Material outlined 風的**浮動標籤**。玻璃框折射(同 search),floating label 純 CSS;**唯一的 JS** 是清除鈕的點擊動作(單一委派監聽)。

### 結構

```html
<div class="lg-field">
  <div class="lg lg-field__box" data-lg>
    <input id="f1" class="lg-field__input" type="email" placeholder=" ">
    <label for="f1" class="lg-field__label">電子郵件</label>
    <button type="button" class="lg-field__clear" data-lg-clear aria-label="清除"><svg viewBox="0 0 256 256"><use href="#ph-x"/></svg></button>
  </div>
  <span class="lg-field__hint">我們不會分享你的信箱</span>
</div>
```

- 外層 `.lg-field`(非玻璃,版型 + 狀態載體):`display:flex; flex-direction:column; gap:6px`。
- **玻璃只在 `__box`**:`class="lg lg-field__box" data-lg`(折射,同 `.lg-search`),`--lg-radius-m`、`position:relative`、`min-height` 約 54–56px、左右 padding 14px。
- **真 `<label for>`**(無障礙 ✓),絕對定位浮在框內。
- `placeholder` **必須是一個空格 `" "`**(floating 機制靠 `:placeholder-shown` 偵測「空」)。
- 清除鈕用既有圖示 `#ph-x`(icons.json 已有,**不需新增圖示**);引用完整字面量 `'#ph-x'`。
- hint 是實心內容層(helper / error 文字)。

### 浮動標籤機制(純 CSS,零 JS)

label 在 `__box` 內垂直置中(`position:absolute; left:14px; top:0; height:100%; display:flex; align-items:center;`),只動 `transform` + `color`(避免 % 與 px 互轉的不平滑;不動 `top`):

- **靜止態(空且未聚焦)**:`.lg-field__input:placeholder-shown:not(:focus) + .lg-field__label` → `transform:none`、`font-size:15px`、`color:var(--lg-text-dim)`(看似置中 placeholder)。
- **上浮態(聚焦或有值)**:`.lg-field__input:focus + .lg-field__label`、`.lg-field__input:not(:placeholder-shown) + .lg-field__label` → `transform: translateY(-15px) scale(.78)`、`transform-origin:left center`、`color:var(--lg-accent)`。
- DOM 順序 input→label,用相鄰 `+`;**不引入 `:has()`**。
- input 上方留白避免與上浮 label 重疊:`.lg-field__input { padding:20px 0 4px; }`(text 偏下;確切 px 於 Chromium 微調)。
- 過渡:`transition: transform var(--lg-speed) var(--lg-ease-out), color var(--lg-speed) var(--lg-ease-out);`

### 清除鈕

- **顯示時機純 CSS**:`.lg-field__input:placeholder-shown ~ .lg-field__clear { display:none; }`(空時隱藏,有值才出現;clear 在 input 之後,用一般兄弟 `~`)。
- 樣式:小圓鈕(約 24px),`color:var(--lg-text-dim)`,hover 提亮;`flex:none`,靠右。
- **點擊動作(本元件唯一 JS)**:在 `liquid-glass.js` 的 init/boot 註冊**一個**委派 click 監聽:點到 `[data-lg-clear]` → 找同一 `.lg-field__box` 內的 `.lg-field__input` → 清空 `value`、`dispatchEvent(new Event('input',{bubbles:true}))`(讓 `:placeholder-shown` 重新生效並通知框架)、`input.focus()`。零 per-instance JS;非 Chromium 同樣運作(純 DOM)。

### 狀態

| 狀態 | 視覺 | 驅動 |
|---|---|---|
| 靜止 | 折射玻璃框 + inset 細描邊(`--lg-stroke-soft`);label 置中 dim | 預設 |
| hover | 描邊略提亮(`--lg-stroke`) | `.lg-field__box:hover` |
| focus | box accent ring + label 上浮轉 accent。ring 用 `box-shadow`(跟隨圓角),**須保留 `.lg` 基底陰影**:`box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent);`(`.lg` 已給 `var(--lg-shadow)` 與 `.lg::before` inset stroke,**勿重設/重畫**) | `.lg-field__box:focus-within` + label float 規則 |
| **error** | `.lg-field--error` → ring / label / hint 全轉 `--lg-down`(#d2503e,既有紅 token);**error 壓過 focus**(規則置於 focus 之後、特異度 ≥;ring = `var(--lg-shadow), 0 0 0 2px var(--lg-down)`) | `.lg-field--error` 後代選擇器 |
| disabled | `.lg-field--disabled .lg-field__box { opacity:.5; }` + `.lg-field--disabled .lg-field__input { cursor:not-allowed; }`(見下) | `.lg-field--disabled` 修飾類 |
| readonly | native `readonly`:框略淡、`:focus-within` 不顯 accent ring(改用 base 中性 ring) | `.lg-field__input:read-only` |

**disabled 處理(定案,不引入 `:has()`):** input 在 box 內(非兄弟),無法用 `~`。採**修飾類** `.lg-field--disabled`(consumer 與 native `disabled` 屬性同加)淡化整框——與 Checkbox 的「避開 :has()」一致。

### 玻璃 / token

- `lg + data-lg` 折射框,`--lg-radius-m`;dense 表單可改 `lg-static`(磨砂、便宜)——文件註記,v1 demo 用折射。
- 全用既有 token:`--lg-accent` / `--lg-down` / `--lg-down-soft` / `--lg-tint` / `--lg-stroke` / `--lg-stroke-soft` / `--lg-text` / `--lg-text-dim` / `--lg-radius-m` / `--lg-font` / `--lg-speed` / `--lg-ease-out`。不硬編顏色。

### 範圍邊界(YAGNI,v1 不做)

- **不做**:leading 前置圖示、尺寸變體(--sm)、無標籤(label-less)變體、trailing 單位/前綴、字數計數。
- **floating label 是本件的核心形態**:v1 假設 label 一定在(showcase 也用 label)。label-less 之後再開。
- Textarea(#2)是**獨立下一件**:複用 `__box` + 浮動標籤,換 `<textarea>`、無清除鈕、可垂直拉高——不在本 spec。

### 整合位置

1. CSS 進 `liquid-glass.css`,作為**第 7b 節「文字輸入 .lg-field」緊接第 7 節 `.lg-search` 之後**(同屬輸入框家族,~348 行後、第 8 節 `.lg-switch` 之前);reduced-motion 區(~935 行,`.lg-switch__thumb` 那塊)補 `.lg-field__label { transition-duration:0.01s !important; }`。
2. JS:`liquid-glass.js` init/boot 註冊單一 `[data-lg-clear]` 委派監聽。
3. `site.src.html` 元件展示加 Text field tile:至少「空(label 置中)/ 有值(label 上浮 + 清除鈕)/ error / disabled」數態,疊在有色或圖像背景上(折射要有背景才顯)。
4. CLAUDE.md AI 規格書「元件結構」段補 `文字輸入` 一行 + 「JS API」若有需要;AI Guide 分頁「元件程式碼庫」補片段。
5. `python3 build_site.py` 重生 `index.html`,Chromium 自驗(折射顯影、label 上浮平滑、清除鈕顯隱與清空、error 紅、focus ring、降級不報錯)。

### 驗收

- 空欄:label 置中如 placeholder;聚焦 → label 平滑上浮轉 accent、框顯 accent ring。
- 打字 → 清除鈕出現;點清除 → 清空、label 落回(若失焦)、input 重新聚焦、不報錯。
- `.lg-field--error`:ring / label / hint 轉紅;聚焦時仍維持紅(error 壓過 focus)。
- `.lg-field--disabled` + `disabled`:整框淡、not-allowed。`readonly`:可選取不可改、無 accent ring。
- 非 Chromium:磨砂降級、floating label 與清除動作正常、無 console 錯誤。
- reduced-motion:label 切換無過渡突跳。

### 風險

中。比 Checkbox 高:(1) floating label 與 input padding 的垂直對位需 Chromium 微調(spec 給目標值,實作於視覺 gate 收斂);(2) 折射框顯影同既有 search;(3) 清除鈕委派監聽要正確定位同框 input 並派發 input 事件。皆有既有範式(search 折射框、kit 既有委派/事件模式)。
