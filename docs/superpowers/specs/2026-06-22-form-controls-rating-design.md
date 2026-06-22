# 表單控制家族 A — Rating 設計 spec

> 對象:Liquid Glass Kit v0.1,家族 A 第六件(#9)。
> 家族共同決策見 Checkbox spec。
> 節奏:做完 build + Chromium 自驗 → 交使用者目視 → 核可。留在 `feat/form-family-a`。
> 日期:2026-06-22。

## Rating · `.lg-rating`(星等評分)

**定位:** 5 顆星 radio 評分。**純 CSS、零 JS**:經典「reverse DOM order + `~` 選擇器」hover 預覽 + 點選。radio value = 分數(進表單、原生鍵盤方向鍵)。用既有 `#ph-star-fill`,**無新圖示**。

### 不是玻璃(誠實標註)

星星是**實心內容層的圖示**(像儀表板數字),**rating 本身不上玻璃**——星評分無容器需求。demo 擺在玻璃 tile 上即可。

### 結構(星 5→1 **DOM 倒序**,`flex-direction:row-reverse` 視覺正序)

```html
<div class="lg-rating" role="radiogroup" aria-label="評分">
  <input type="radio" name="rate" id="rate5" value="5"><label for="rate5" class="lg-rating__star" aria-label="5 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
  <input type="radio" name="rate" id="rate4" value="4"><label for="rate4" class="lg-rating__star" aria-label="4 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
  <input type="radio" name="rate" id="rate3" value="3"><label for="rate3" class="lg-rating__star" aria-label="3 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
  <input type="radio" name="rate" id="rate2" value="2"><label for="rate2" class="lg-rating__star" aria-label="2 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
  <input type="radio" name="rate" id="rate1" value="1"><label for="rate1" class="lg-rating__star" aria-label="1 星"><svg viewBox="0 0 256 256"><use href="#ph-star-fill"/></svg></label>
</div>
```

- 每星 = `<input type=radio>` 緊接其 `<label>`;DOM 順序 **5→1**;容器 `display:inline-flex; flex-direction:row-reverse`(視覺 1→5)。
- radio 隱藏(`position:absolute; opacity:0; width:0; height:0`),仍可鍵盤聚焦/方向鍵。
- 星用單一 `#ph-star-fill`,`fill: currentColor` → 由 label `color` 驅動;off=dim、on=accent。

### 機制(純 CSS 四條規則,**順序與特異度須照抄**)

```css
.lg-rating__star { color: var(--lg-text-dim); }                      /* 1. 預設 dim */
.lg-rating input:checked ~ label { color: var(--lg-accent); }        /* 2. 已選(及更低星)轉 accent */
.lg-rating:hover input ~ label { color: var(--lg-text-dim); }        /* 3. 容器 hover 時全部重置 dim */
.lg-rating:hover label:hover,
.lg-rating:hover label:hover ~ label { color: var(--lg-accent); }    /* 4. hover 預覽:hovered + 更低星轉 accent */
```

- **為何這樣排**:規則 2/3 特異度同為 (0,2,2),規則 3 在後 → 容器 hover 時「重置」勝過「已選」。規則 4 用 `.lg-rating:hover label:hover…` = (0,3,1)/(0,3,2) **高於** 規則 3 (0,2,2) → 預覽(含 hovered 那顆本身)勝過重置。未 hover 時只有規則 2 生效 = 顯示已選分數。`input:checked ~ label` 與 `label:hover ~ label` 的 `~` 是 **DOM 倒序**,故「更低分的星」= 視覺左側。**不引入 `:has()`、零 JS。**
- 液態手感:hover 那顆星 `scale` 彈一下:`.lg-rating:hover label:hover { scale: 1.12; }`(transition `color, scale`)。

### 狀態

| 狀態 | 視覺 | 驅動 |
|---|---|---|
| 已選 | 左起 N 顆 accent | 規則 2 |
| hover 預覽 | 即時顯示滑到第幾顆 + 該顆彈一下 | 規則 3+4 |
| focus-visible | 聚焦的星顯 ring | `.lg-rating input:focus-visible + label { outline: 2px solid var(--lg-accent); outline-offset: 2px }` |
| disabled | `.lg-rating--disabled { opacity:.5; pointer-events:none }`(demo 同時對 radio 加 native `disabled`) | 修飾類 |
| reduced-motion | 星不彈、變色即時 | 補 `.lg-rating__star { transition-duration:0.01s !important }` |

### token / 尺寸

- 星 `svg { width:28px; height:28px; fill:currentColor }`;容器 `gap:2px`;label `cursor:pointer`、`transition: color var(--lg-speed) var(--lg-ease-out), scale var(--lg-speed) var(--lg-ease)`。
- 色:off `--lg-text-dim`、on `--lg-accent`(隨主題自動)。不硬編。

### 範圍邊界(YAGNI,v1 不做)

- 半星、唯讀展示變體(顯示既有平均、不可改)、尺寸變體、5 以外星數(consumer 自己寫幾顆 radio)、清除已選。

### 整合位置

1. CSS 進 `liquid-glass.css`,輸入框家族附近(如 `.lg-stepper` 區之後)新增「.lg-rating」節;reduced-motion 區補 `.lg-rating__star`。
2. JS:無。
3. `site.src.html` 元件展示加 Rating tile(一般:預設選 4 星 + disabled:選 3 星),非玻璃星擺在玻璃 tile 上。
4. CLAUDE.md AI 規格書「元件結構」段補 `星等評分` 一行;AI Guide 程式碼庫補 `<details>`(`data-snippet="rating"`)。
5. `python3 build_site.py` 重生 `index.html`,Chromium 自驗。

### 驗收

- 滑過星星 → 即時預覽到該顆(含該顆變色 + 彈一下);點下 → 固定該分數(離開仍維持)。
- 選 N 星後,左起 N 顆 accent;改點別顆即換分。
- 方向鍵在組內移動選取;聚焦的星有 ring。
- disabled rating:整體淡、不可 hover/點。
- 非 Chromium:星顯示與選取正常(純 DOM/CSS,無折射依賴)、無 console 錯誤。
- reduced-motion:無彈跳。

### 風險

低中。零 JS、零新圖示;唯一風險是 hover-vs-checked 的四條 CSS 規則順序/特異度必須照抄(spec 已給推導),否則 hover 預覽會錯亂。reverse DOM + `~` 是成熟範式。
