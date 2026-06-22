# 表單控制家族 A — Radio group 設計 spec

> 對象:Liquid Glass Kit v0.1,家族 A 第四件(#6)。
> **平行 Checkbox**(`2026-06-21-form-controls-checkbox-design.md`):同版型、同磨砂手法、同 token、同狀態,僅**圓化 box + 改中心圓點**。家族共同決策見 Checkbox spec。
> 節奏:做完 build + Chromium 自驗 → 交使用者目視 → 核可。留在 `feat/form-family-a`,與家族一起合。
> 日期:2026-06-22。

## Radio group · `.lg-radio` / `.lg-radio-group`

**定位:** 單選控制。**零 JS,純 CSS + native `<input type="radio">`**(同 `.lg-check`)。圓形磨砂 box + 中心圓點;圓點用 CSS `::after`,**無新圖示**。多個 radio 共用 `name` → native 單選 + 方向鍵切換。

### 結構

```html
<div class="lg-radio-group" role="radiogroup" aria-label="方案">
  <label class="lg-radio">
    <input type="radio" name="plan" value="free" checked>
    <span class="lg-radio__box"></span>
    <span class="lg-radio__label">免費方案</span>
  </label>
  <label class="lg-radio">
    <input type="radio" name="plan" value="pro">
    <span class="lg-radio__box"></span>
    <span class="lg-radio__label">專業方案</span>
  </label>
</div>
```

- `.lg-radio-group`:薄版型包裹 `display:flex; flex-direction:column; gap:12px`,語意 `role=radiogroup`。
- `.lg-radio`:`<label>` 包隱藏 radio + 圓 box + 文字,**與 `.lg-check` 同版型**(`inline-flex; align-items:center; gap:11px; …`)。
- `.lg-radio__box` 不掛 `data-lg`:bespoke 磨砂(同 `.lg-check__box`/`.lg-switch__track`),`html.lg-fallback` 一併套。

### 視覺與動畫(平行 checkbox,僅兩處差異)

| 狀態 | 視覺 | 驅動 |
|---|---|---|
| unchecked | 磨砂玻璃**圓**(`border-radius:50%`)+ inset 細描邊(`--lg-stroke-soft`),無圓點 | 預設 |
| checked | box 填 `--lg-accent` + **白色中心圓點**(`.lg-radio__box::after`,`scale 0→1` 帶 overshoot 彈入) | `input:checked + .lg-radio__box` |
| hover / active | 描邊提亮(`--lg-stroke`)+ `scale(1.04)` / 按住 `scale(0.92)` | `.lg-radio:hover/active .lg-radio__box` |
| disabled | `opacity:0.45`(box + label) | `input:disabled ~ .lg-radio__box / __label`(兄弟選擇器,**不引入 `:has()`**) |
| focus-visible | `outline: 2px solid var(--lg-accent); outline-offset: 3px` | `input:focus-visible + .lg-radio__box` |
| reduced-motion | 圓點直接出現,無 overshoot | reduced-motion 區補 `.lg-radio__box, .lg-radio__box::after { transition-duration:0.01s !important }`(同 checkbox 同時涵蓋 box scale 與標記) |

**與 checkbox 的兩處差異:**
1. `box` 圓化:`border-radius: 50%`(checkbox 是 `--lg-radius-s`)。
2. 標記:**中心圓點**(`::after`:約 8px 圓、白色、絕對置中、`scale` overshoot)取代 checkbox 的 `__mark` 勾。圓點用 `::after`,**無子元素、無圖示**。

- box 尺寸 22px(同 checkbox);overshoot 用 `cubic-bezier(.34,1.56,.64,1)`;顏色/過渡全用既有 token。
- **無 indeterminate**(radio 無此態)。

### API(宣告式,零 JS)

- 基本:`<div class="lg-radio-group">` 內放多個 `<label class="lg-radio">`(共用 `name`)。放進頁面即可用,**不必 `attach()`**。
- disabled:native `disabled`。

### 範圍邊界(YAGNI,v1 不做)

- 尺寸變體、卡片式 radio(整塊大卡可點)、水平排列預設(consumer 可 inline 覆寫 `flex-direction:row`)。

### 整合位置

1. CSS 進 `liquid-glass.css`,作為**第 8c 節「單選 .lg-radio」緊接第 8b `.lg-check` 之後**;reduced-motion 區(`.lg-switch__thumb` 那塊,已含 `.lg-check__mark`)補 `.lg-radio__box::after`。
2. JS:無。
3. `site.src.html` 元件展示 Checkbox tile 之後加 Radio tile:一組 3 選項(預設選一)+ 一個 disabled,疊在有色/圖像背景上。
4. CLAUDE.md AI 規格書「元件結構」段補 `單選` 一行(核取方塊那行之後);AI Guide 程式碼庫補 `<details>`(`data-snippet="radio"`)。
5. `python3 build_site.py` 重生 `index.html`,Chromium 自驗。

### 驗收

- 點某選項 → 該圓填 accent + 白圓點彈入,同組其他選項自動取消(native 單選)。
- 方向鍵在組內移動選取(native radio 行為)。
- disabled 選項半透明、不可選;focus-visible 有 ring;hover/active 有縮放回饋。
- 非 Chromium:磨砂降級 + native radio 正常,無 console 錯誤。
- reduced-motion:圓點無 overshoot 突跳。

### 風險

低。純 CSS、零 JS、零新圖示、零新依賴,且平行已驗收的 `.lg-check`。唯一新東西是圓化 box 與 `::after` 圓點,需 Chromium 確認磨砂與圓點手感。
