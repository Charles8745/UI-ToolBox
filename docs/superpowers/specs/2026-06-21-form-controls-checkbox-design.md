# 表單控制家族 A — Checkbox 設計 spec

> 對象:Liquid Glass Kit v0.1。新增「表單 / 輸入控制」家族(HANDOFF.md 路線圖 A 段)。
> 節奏:**一次一件,逐件 build + Chromium 實機自驗 → 交使用者檢查 → 核可才做下一件**(沿用 iOS 26 那批的 SDD 流程)。
> 本 spec 只涵蓋**第一件:Checkbox**。後續每件(Text field → Textarea → Segmented control …)各自再開 spec。
> 日期:2026-06-21。

## 家族 A 共同決策(後續各件共用,寫一次)

- **玻璃只做控制層**:輸入框外框 / 分段藥丸 / checkbox 方塊是玻璃層;使用者打的字、勾選的勾是**實心內容層**(鐵律 5)。
- **小型 / 大量重複的元件**(checkbox 方塊、radio、chip 類)用 **bespoke 磨砂**(直接 `backdrop-filter: blur()`,同 `.lg-switch__track` 手法)或 `lg-static`,**不掛 `data-lg`**(不折射、便宜);**大框**(text field、textarea)再評估是否上 `data-lg` 折射。
- **API 宣告式**:沿用 `class="lg …"` + `data-lg-*`;行為(若需要)進 `liquid-glass.js`,沿用既有 `Spring` / `springOnVisible` / 單一 `MutationObserver` 屬性路由,**勿另起爐灶**。
- **樣式進 `liquid-glass.css`**;新圖示先進 `assets/icons.json`,引用用完整字面量。
- **降級**:非 Chromium 自動走磨砂;native input 本身可用,各件需確保不報錯。
- **reduced-motion**:沿用既有慣例(定態 / 直接顯示,不自動動)。
- **能力邊界**:折射顯影、磨砂降級在程式環境無法渲染驗證,只能 Chromium 實機 + 交使用者檢查。
- **每件完成步驟**:CSS/JS → `site.src.html` 元件分頁加實機展示(疊在有色/圖像背景上才看得見)→ CLAUDE.md AI 規格書 + AI Guide 分頁「元件程式碼庫」補段落 → `python3 build_site.py` 重生 `index.html`。

---

## Checkbox · `.lg-check`

**定位:** 家族 A 第一件,最簡單的暖身件。**零 JS** — 純 CSS + native checkbox 驅動(同 `.lg-switch`)。

### 結構

```html
<label class="lg-check">
  <input type="checkbox">
  <span class="lg-check__box">
    <svg class="lg-check__mark" viewBox="0 0 256 256"><use href="#ph-check"/></svg>
  </span>
  <span class="lg-check__label">記住我</span>
</label>
```

- 沿用 `.lg-switch` 版型:`<label>` 包 hidden native `<input>`(`position:absolute;opacity:0`)+ 視覺 `__box` + 文字 `__label`。
- 圖示用既有 `#ph-check`(icons.json 已有),**不需新增圖示**。
- `__box` **不掛 `data-lg`**:bespoke 磨砂(`backdrop-filter: blur() saturate()`,同 `.lg-switch__track`),`html.lg-fallback` 一併套(降級自動生效),零 JS / 不必 `attach()`。

### 狀態與動畫

| 狀態 | 視覺 | 驅動 |
|---|---|---|
| unchecked | 磨砂玻璃框 + `inset` 細描邊(`--lg-stroke-soft`),無勾 | 預設 |
| checked | `__box` 填 `--lg-accent`(同 switch 開啟);白勾 `scale 0→1` 帶輕微 overshoot 彈入 | `input:checked + .lg-check__box` |
| indeterminate | `__box` 填 accent,顯示一條白橫槓(CSS `::after` bar,**免圖示**);隱藏勾 | `input:indeterminate + .lg-check__box`(consumer 設 `el.indeterminate=true`) |
| hover | 描邊提亮、`__box` `scale(1.04)` | `.lg-check:hover` |
| active(按住) | `__box` `scale(0.92)` 液態擠壓,放開回彈 | `.lg-check:active` |
| disabled | `opacity:0.45` + `cursor:not-allowed`(box + label) | `input:disabled ~ .lg-check__box` / `~ .lg-check__label`(兄弟選擇器,**不引入 `:has()`**,codebase 尚未用到) |
| focus-visible | `outline: 2px solid var(--lg-accent); outline-offset: 3px`(同 switch) | `input:focus-visible + .lg-check__box` |
| reduced-motion | 勾直接出現,無 overshoot / scale 過渡 | 在既有 `.lg-switch__thumb` 那個 reduced-motion 區塊(liquid-glass.css ~931/935 行)補 `.lg-check__mark, .lg-check__box { transition-duration: 0.01s !important; }` |

- 勾的 overshoot 用 `cubic-bezier(.34,1.56,.64,1)`(back-out,輕微回彈);與 switch thumb 過渡同調。indeterminate 與 checked 並存時(罕見/無效態)以 `:indeterminate` 為準:`input:indeterminate + .lg-check__box .lg-check__mark { scale: 0 }`,只顯橫槓。
- box 尺寸:**22px** 方塊,`--lg-radius-s` 圓角;mark 內縮置中。
- 顏色 / 圓角 / 字型全用既有 token(`--lg-accent` / `--lg-tint` / `--lg-stroke-soft` / `--lg-text` / `--lg-radius-s` / `--lg-font`),不硬編。

### API(宣告式,零 JS)

- 基本:`<label class="lg-check">…</label>` — 放進頁面即可用,**不必呼叫 `attach()`**。
- indeterminate:consumer JS 設 `input.indeterminate = true`(標準 DOM property,非本套 API)。
- disabled:native `disabled` 屬性。

### 範圍邊界(YAGNI,v1 不做)

- **不做**尺寸變體(`--sm`/`--lg`)、error 狀態、`.lg-check-group` 包裹器(多個直接堆疊,分組只是 flex 版型)。
- 這些日後若有需求再加,不阻擋 v1。

### 整合位置

1. CSS 進 `liquid-glass.css` 第 8 節(`.lg-switch` 之後),並在尾段 reduced-motion 區補對應覆寫。
2. `site.src.html` 元件分頁 controls 區(switch / slider 旁)加實機展示:至少 unchecked / checked / indeterminate / disabled 各一,疊在有色或圖像背景上。
3. CLAUDE.md AI 規格書「元件結構」段補 `核取方塊` 一行;AI Guide 分頁「元件程式碼庫」補對應 HTML 片段。
4. `python3 build_site.py` 重生 `index.html`,Chromium 實機自驗(折射 N/A;檢查磨砂、勾動畫、accent 填色、focus ring、降級不報錯)。

### 驗收

- 勾選 → accent 填色 + 白勾彈入;再點 → 收回。
- `indeterminate=true` → 顯示橫槓;點擊後轉為一般 checked/unchecked。
- disabled 不可點、半透明;focus-visible 有 ring;hover/active 有液態縮放回饋。
- 非 Chromium:磨砂底 + native checkbox 行為正常,無 console 錯誤。
- reduced-motion:無過渡突跳。

### 風險

低。純 CSS、零 JS、零新圖示、零新依賴。唯一需 Chromium 實看的是磨砂質感與勾動畫手感。
