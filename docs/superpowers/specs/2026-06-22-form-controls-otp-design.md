# 表單控制家族 A — OTP 設計 spec

> 對象:Liquid Glass Kit v0.1,家族 A 第七件(#10)。
> 家族共同決策見 Checkbox spec。本件用 per-container init(同 `initTabs`/`initDock`)。
> 節奏:做完 build + Chromium 自驗 → 交使用者目視 → 核可。分支 `feat/form-family-a2`(承接 A 家族;之後 #11 File upload 可同分支累積再合)。
> 日期:2026-06-22。

## OTP · `.lg-otp`(驗證碼分格)

**定位:** N 個單字元格,輸入自動進格 / 退格回格 / 貼上分配。native `<input maxlength="1">`(進表單、行動數字鍵盤)。**無新圖示**。

### 格子為何用 bespoke 磨砂 input(技術邊界)

`<input>` 元素**無法產生 `::before`/`::after`**,而 `.lg` 的鏡面 rim 靠 `.lg::before`。故格子**不**用 `.lg`/`data-lg`,改用 **bespoke 磨砂 input**(直接 `backdrop-filter: blur() saturate()`,同 `.lg-check__box`/`.lg-switch__track`),格子自定義 `box-shadow`(不涉及 `.lg` 基底陰影);focus 時加 accent ring。降級自動。

### 結構

```html
<div class="lg-otp" role="group" aria-label="驗證碼">
  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" autocomplete="one-time-code" aria-label="第 1 碼">
  <input class="lg-otp__cell" type="text" inputmode="numeric" maxlength="1" aria-label="第 2 碼">
  … 共 6 格 …
</div>
```

- `.lg-otp` 容器:`display:inline-flex; gap:8px`。
- `.lg-otp__cell`:磨砂方框(約 46×54px)、置中大字、`outline:none`、focus accent ring。預設 6 格(consumer 要幾位就寫幾個 input);`inputmode="numeric"`、`autocomplete="one-time-code"`(行動裝置自動填碼)。

### 行為(JS = `initOtp(container)`,每個 `.lg-otp` 一份)

在 `boot()` 用 `[].forEach.call(document.querySelectorAll('.lg-otp'), initOtp)` 初始化(同 `initTabs`/`initDock`/`initSlider` per-container 範式)。`initOtp(otp)`:

- 取 `cells = otp.querySelectorAll('.lg-otp__cell')`。
- **input 事件**:該格若多於 1 字(防 maxlength 被繞過)只留最後一字;若有值且有下一格 → focus 下一格。
- **keydown Backspace**:該格為空時 → focus 上一格並**清掉上一格的值**(連續退格往回刪),`preventDefault`。
- **paste 事件**:`preventDefault`,取剪貼簿文字、去空白,**從第一格起**逐字填入各格,focus 落在最後填入的格。
- native 左右鍵移動、點某格直接改皆保留。

### 值

- v1:各格 input 即值,consumer 讀 `.lg-otp` 內所有 `.lg-otp__cell` 的 value 串接。**不**另設隱藏彙總 input(YAGNI)。

### 狀態

| 狀態 | 視覺 | 驅動 |
|---|---|---|
| 預設 | 磨砂方框 + inset 細描邊 | `.lg-otp__cell` |
| focus | accent ring:`box-shadow: var(--lg-shadow-soft), inset 0 0 0 1px var(--lg-stroke-soft), 0 0 0 2px var(--lg-accent)`(格子自有陰影,**非** `.lg` 基底,故直接重寫即可) | `.lg-otp__cell:focus` |
| disabled | native `disabled`:`.lg-otp__cell:disabled { opacity:.5; cursor:not-allowed }`(input 原生支援 `:disabled`,免修飾類) | `:disabled` |
| reduced-motion | focus ring 過渡即時 | 補 `.lg-otp__cell { transition-duration:0.01s !important }` |

### 範圍邊界(YAGNI,v1 不做)

- 倒數計時 / 重送、驗證 API、字元遮罩(密碼點)、只允許數字的硬性過濾(`inputmode` 已給數字鍵盤;貼上保留原字元,支援英數碼)、隱藏彙總 input、自動提交。
- **不做「滿格覆寫」**(使用者決定):`maxlength="1"` 下,已填格再輸入會被擋,需先 Backspace 才能改——這是**刻意的 v1 行為**(自動進格下少遇到),非缺陷。要覆寫需另加 keydown 處理,留待之後。

### 整合位置

1. CSS 進 `liquid-glass.css`,輸入框家族附近(如 `.lg-rating` 區之後)新增「.lg-otp」節;reduced-motion 區補 `.lg-otp__cell`。
2. JS:`liquid-glass.js` 加 `initOtp(container)`(放 `initSteppers` 附近),`boot()` 加 `[].forEach.call(document.querySelectorAll('.lg-otp'), initOtp)`。
3. `site.src.html` 元件展示加 OTP tile(一般 6 格 + disabled 6 格,疊在有色/圖像背景上)。
4. CLAUDE.md AI 規格書「元件結構」段補 `驗證碼` 一行;AI Guide 程式碼庫補 `<details>`(`data-snippet="otp"`)。
5. `python3 build_site.py` 重生 `index.html`,Chromium 自驗。

### 驗收

- 連打 6 碼 → 每打一碼自動跳下一格;退格在空格 → 回上一格並清掉;貼上 6 碼 → 自動分配 6 格、focus 末格。
- 左右鍵/點擊可移動;focus 格有 accent ring。
- disabled 格:半透明、不可輸入。
- 非 Chromium:磨砂降級、自動進格/退格/貼上正常(純 DOM)、無 console 錯誤。
- reduced-motion:focus ring 無過渡突跳。

### 風險

低中。新東西:`initOtp` 的三行為(input 進格 / backspace 回格清值 / paste 分配)+ bespoke 磨砂 input。皆有既有範式(per-container init、bespoke 磨砂同 checkbox)。
