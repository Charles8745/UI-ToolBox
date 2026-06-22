# 表單控制家族 A — Textarea 設計 spec

> 對象:Liquid Glass Kit v0.1,家族 A 第三件。
> **複用 Text field**(`2026-06-22-form-controls-text-field-design.md`)的 `.lg-field` / `.lg-field__box` / 浮動標籤 / 狀態 / token,本件只描述**差異(`--area` 修飾)**。家族共同決策見 Checkbox spec。
> 節奏:做完 build + Chromium 自驗 → 交使用者目視 → 核可。留在 `feat/form-family-a`,與家族一起合。
> 日期:2026-06-22。

## Textarea · `.lg-field--area`(多行輸入)

**定位:** 多行文字輸入。**複用 Text field 的 `.lg-field` 殼**(DRY),只加修飾類 `.lg-field--area`,把 `<input>` 換成 `<textarea>`。**零新 JS、零新圖示**(無清除鈕)。

### 結構

```html
<div class="lg-field lg-field--area">
  <div class="lg lg-field__box" data-lg>
    <textarea id="t1" class="lg-field__input" placeholder=" " rows="3"></textarea>
    <label for="t1" class="lg-field__label">訊息內容</label>
  </div>
  <span class="lg-field__hint">最多 500 字</span>
</div>
```

- `<textarea>` 一樣掛 `.lg-field__input` → 繼承既有輸入框樣式(`border:0; background:transparent; outline:none; color:var(--lg-text)`)與浮動標籤的相鄰 `+` 選擇器(`:placeholder-shown` 對 `<textarea>` 同樣有效)。
- `placeholder` 仍**必須是一個空格 `" "`**。
- **無清除鈕**;`rows` 由 consumer 設初始高度。

### 與 Text field 的差異(全靠 `.lg-field--area` 修飾,複用其餘)

1. **label 靜止貼頂**:單行 label 垂直置中(`top:0; height:100%`);textarea 文字從頂部起,故靜止 label 改貼**首行**:
   `.lg-field--area .lg-field__label { top: 22px; height: auto; transform-origin: left top; }`
   覆寫 base 的 `top:0; height:100%`,讓 label 只有文字高度、定位在首行(22px)。**用 `top` 定位而非在全高元素上加 padding**——否則 `scale(.78)` 會連整個全高元素一起縮、浮動位置依賴框高且隨 resize 漂移。上浮 transform **複用** Text field 既有規則 `translateY(-16px) scale(.78)` + `transform-origin:left top`(從首行 22px 縮到框上緣約 6px,與框高無關);確切 px 於 Chromium 微調。
2. **多行 + 可垂直 resize**:
   `.lg-field--area .lg-field__input { resize: vertical; min-height: 96px; padding: 22px 0 10px; line-height: 1.45; }`
   `.lg-field__box` 既有 `align-items:stretch` 讓 textarea 撐滿框;resize 時 box 隨之長高、label(絕對定位 top)不動。

### 沿用(不重做,複用 Text field)

- 浮動標籤機制(`placeholder=" "` + `:placeholder-shown`/`:focus`,相鄰 `+`,只動 transform+color)。
- **陰影紀律**:`.lg-field__box` 不重設 base box-shadow / 不重畫 inset stroke;focus ring `:focus-within` = `box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent)`;hover 由 `.lg:hover::after` sheen 負責。
- 狀態:error(`.lg-field--error` → `--lg-down`,壓過 focus)、disabled(`.lg-field--disabled`)、readonly(`:read-only` 淡字)、reduced-motion(`.lg-field__label` 過渡縮短,已含)。
- 玻璃只在 `__box`(`lg + data-lg`);token 同 Text field;不引入 `:has()`。

### 範圍邊界(YAGNI,v1 不做)

- 字數計數器、auto-grow(自動長高需 JS)、鎖死不可 resize 變體。

### 整合位置

1. CSS:在 `liquid-glass.css` **第 7b 節 `.lg-field` 規則尾端追加 `.lg-field--area` 兩條規則**(同檔同節,緊接既有 `.lg-field` 規則之後)。**reduced-motion 無需新增**(`.lg-field__label` 已在內)。
2. **JS:無**(無清除鈕,不需委派)。
3. `site.src.html` 元件展示 Text field tile 之後加 Textarea tile:空態(label 貼頂)+ 有值態(label 上浮、多行),疊在有色/圖像背景上。
4. CLAUDE.md AI 規格書「元件結構」段補 `多行輸入` 一行(文字輸入那行之後);AI Guide 程式碼庫補 `<details>` 一條(`data-snippet="textarea"`)。
5. `python3 build_site.py` 重生 `index.html`,Chromium 自驗。

### 驗收

- 空態:label 貼**首行**位置如 placeholder;聚焦 → label 平滑上浮到框上緣、轉 accent、框顯 accent ring。
- 有值/多行:label 維持上浮;內容多行正常換行;**右下角可垂直拖拉變高**,label 不隨之移動。
- error / disabled / readonly:沿用 Text field 行為(紅 ring/label/hint、整框淡、淡字)。
- 非 Chromium:磨砂降級、浮動標籤與 resize 正常、無 console 錯誤。
- reduced-motion:label 切換無突跳。

### 風險

低。複用既成的 `.lg-field` 殼;唯一新東西是 `--area` 的 label 貼頂與 textarea 內距/resize 的垂直對位,需 Chromium 微調(spec 給目標值)。無新 JS、無新圖示、無新依賴。
