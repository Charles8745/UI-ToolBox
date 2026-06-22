# 表單控制家族 A — Stepper 設計 spec

> 對象:Liquid Glass Kit v0.1,家族 A 第五件(#7)。
> 家族共同決策見 Checkbox spec。本件用既有 JS 委派範式(同 `initClearFields`)。
> 節奏:做完 build + Chromium 自驗 → 交使用者目視 → 核可。留在 `feat/form-family-a`。
> 日期:2026-06-22。

## Stepper · `.lg-stepper`(加減步進數字)

**定位:** 數字步進輸入。玻璃 pill 容器 + [− 鈕] [native `<input type=number>`] [+ 鈕]。值用 native number input(可打字、進表單、min/max/step、上下鍵);−/+ 鈕由**單一委派監聽**驅動。用既有 `#ph-minus` / `#ph-plus`,**無新圖示**。

### 結構

```html
<div class="lg lg-stepper" data-lg>
  <button type="button" class="lg-stepper__btn" data-lg-step="-1" aria-label="減少">
    <svg viewBox="0 0 256 256"><use href="#ph-minus"/></svg>
  </button>
  <input class="lg-stepper__input" type="number" value="1" min="0" max="10" step="1" aria-label="數量">
  <button type="button" class="lg-stepper__btn" data-lg-step="1" aria-label="增加">
    <svg viewBox="0 0 256 256"><use href="#ph-plus"/></svg>
  </button>
</div>
```

- 容器 `lg + data-lg`(折射玻璃),**pill 形**(`--lg-radius-pill`);`display:flex; align-items:center`。
- 玻璃只做容器;數字是實心內容層。`.lg > *` 既有規則使鈕/input 墊在高光層之上、`.lg::before/::after` 為 `pointer-events:none` 故鈕可點(同 field 清除鈕)。
- `<input type="number">`:置中、透明底、無框;**隱藏原生上下箭頭**:
  `.lg-stepper__input::-webkit-outer-spin-button, ::-webkit-inner-spin-button { -webkit-appearance:none; margin:0; }` + `appearance:textfield`。

### 行為(JS = 一個委派監聽,同 `initClearFields` 範式)

- `liquid-glass.js` 新增 `initSteppers()`:在 boot 註冊**一個**委派 click 監聽:
  - 點到 `[data-lg-step]` → 找同 `.lg-stepper` 容器內的 `.lg-stepper__input`;
  - 若 `input.disabled` → 略過;
  - 讀 `data-lg-step` 整數 `n`:`n>0` → `input.stepUp(n)`、`n<0` → `input.stepDown(-n)`(**native 自動 clamp 在 min/max、遵守 step**);
  - `input.dispatchEvent(new Event('input',{bubbles:true}))`。
- 零 per-instance JS;native input 仍可打字、上下鍵——不靠 JS。非 Chromium 同樣運作(純 DOM)。

### 狀態

| 狀態 | 視覺 | 驅動 |
|---|---|---|
| 預設 | 折射 pill 玻璃容器(邊框/陰影沿用 `.lg` 基底,**不重設**) | `.lg` |
| 鈕 hover / active | `.lg-stepper__btn` 提亮(`background:var(--lg-tint)`、`color:var(--lg-text)`)/ 按住 `scale(0.9)` | `.lg-stepper__btn:hover/active` |
| focus | 容器 accent ring,**須保留 `.lg` 基底陰影**:`box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent)`(同 field;`.lg` 已給 `var(--lg-shadow)`、`.lg::before` 給 inset stroke,勿重設/重畫) | `.lg-stepper:focus-within` |
| disabled | `.lg-stepper--disabled` 修飾類 → 整體 `opacity:.5`;demo 同時對 input + 兩鈕加 native `disabled`(JS 亦 guard `input.disabled`) | `.lg-stepper--disabled` |

### API

- 宣告式:`<div class="lg lg-stepper" data-lg>` + 兩個 `data-lg-step="±1"` 鈕 + native number input。動態插入呼叫 `LiquidGlass.attach(el)`(折射);委派監聽全域一次,**新鈕無需額外綁定**。
- 數值/範圍/步進:native `value` / `min` / `max` / `step`。

### 範圍邊界(YAGNI,v1 不做)

- **min/max 時自動 disable −/+ 鈕**(native 已 clamp,點到底無反應;要做需再加 input 監聽更新鈕態)→ 先不做。
- 尺寸變體、長按連續增減、小數/貨幣格式化。

### 整合位置

1. CSS 進 `liquid-glass.css`,輸入框家族附近(如 `.lg-field` 區之後)新增「.lg-stepper」節。`.lg-stepper__btn` 帶 `transition: scale/background/color var(--lg-speed) var(--lg-ease-out)`(平滑回饋);故 reduced-motion 區補 `.lg-stepper__btn { transition-duration:0.01s !important }`。
2. JS:`liquid-glass.js` 加 `initSteppers()`(委派),在 `boot()` 內 `initClearFields();` 之後呼叫。
3. `site.src.html` 元件展示加 Stepper tile(一般 1 個 + disabled 1 個),疊在有色/圖像背景上(折射要有背景)。
4. CLAUDE.md AI 規格書「元件結構」段補 `步進器` 一行 + 「屬性」段補 `data-lg-step`;AI Guide 程式碼庫補 `<details>`(`data-snippet="stepper"`)。
5. `python3 build_site.py` 重生 `index.html`,Chromium 自驗。

### 驗收

- 點 + / − → 數字加減一步,clamp 在 min/max、遵守 step;直接在框內打字也生效;上下鍵可調。
- 鈕 hover/active 有回饋;容器聚焦顯 accent ring(且保留玻璃陰影、不破玻璃邊);折射顯影。
- disabled stepper:整體淡、鈕與 input 不可動。
- 非 Chromium:磨砂降級、−/+ 與打字正常、無 console 錯誤。

### 風險

低中。新東西:native spinner 隱藏(跨瀏覽器)、`initSteppers` 委派(定位同容器 input、native stepUp/stepDown clamp)、容器 focus ring 須保留 `.lg` 基底陰影(沿用 field 已驗證手法)。皆有既有範式。
