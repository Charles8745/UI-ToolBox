# iOS 26 行為升級 — 設計 spec

> 對象:Liquid Glass Kit v0.1。把 iOS 26 招牌「行為」加進**既有元件**(非新增元件)。
> 來源:HANDOFF.md「iOS 26 招牌行為」表 B1–B6。
> 日期:2026-06-21。

## 範圍

做五項,**B2(Bottom accessory)暫跳過**(依賴尚未開發的 backlog #14 Bottom tab bar,待 #14 完成後另開)。

**開發順序(簡單→難):** B4 → B6 → B1 → B5 → B3。

五項各自可單獨出貨 → **一份 spec + 一份分五階段帶檢查點的計畫**。每項做完 build + Chromium 實機自驗,再交使用者檢查,核可後才動下一項。唯一的共用基建(scroll util)在 **B1 階段建立**(B1 是第一個用到的人),B5 沿用;B1 仍可獨立出貨。

## 鐵律(遵守 CLAUDE.md)

- 行為進 `liquid-glass.js`、樣式進 `liquid-glass.css`。
- 沿用既有 `Spring` / `springOnVisible`(IntersectionObserver)/ 單一 `MutationObserver` 屬性路由 / `ResizeObserver`,**勿另起爐灶**。
- 新圖示先進 `assets/icons.json`,引用用完整字面量。
- 玻璃只做控制層;內容(數字/圖/文)是實心層,不上玻璃。
- 改完跑 `python3 build_site.py` 重生 `index.html`;`site.src.html` 對應分頁加實機展示;CLAUDE.md 的 AI 規格書補對應段落。
- `prefers-reduced-motion` 沿用既有 `REDUCED_MOTION` 慣例(亮/定態但不自動動)。

## 能力邊界(誠實標註)

折射顯影、磨砂降級、morph 縮放中的合成穩定性,**在程式環境無法渲染驗證**,只能 Chromium 實機截圖 + 交使用者檢查。非 Chromium(`LiquidGlass.supported === false`)走磨砂降級,各行為需確保不報錯。

## 共用基建(於 B1 階段建立,B5 沿用)

**rAF 合批 scroll util**(避免 B1、B5 各開一個 listener):
- 單一 window scroll listener,rAF 合批,提供 `lastY` / `deltaY` / 方向。
- 訂閱者(B1 的 shrink、B5 的 edge 判斷)註冊回呼,每幀拿到捲動狀態。
- B5 若監聽指定容器,容器各自一份輕量訂閱(同一套工具,target 可換)。
- 在 B1 階段隨 `initScrollShrink()` 一併落地;B5 直接 import,不重複造 listener。

---

## B4 · 同心圓角(JS 自動推算)

**API:** `data-lg-concentric`(opt-in;預設不啟動,避免誤傷刻意設計)。

**做法:**
- 在 `attach()` 末尾,若元素帶 `data-lg-concentric`:找**最近的 lg 父容器**,讀其 computed `border-radius`。
- 四邊 gap 各算:`gapLeft = child.left − parent.left − parentBorderLeft`,top/right/bottom 同理。
- 一個**角**由相鄰兩邊定義,故 `角 inset = max(相鄰兩邊 gap)`(取大者確保半徑不溢出;padding 均勻時兩邊相等,退化為單一 inset)。
- `子角半徑 = max(父對應角半徑 − 角 inset, 最小值)`,四角分別寫進 `el.style.borderRadius`。
- **父無明確圓角、或找不到 lg 父層 → no-op 不寫入。**
- 沿用既有 `ResizeObserver` 在尺寸變動時重算。

**順手修(收進 token 體系):** `.lg-dock__item`(硬編 14px)、`.lg-tooltip`(硬編 13px)→ 改用 `--lg-radius-*`。

**驗收:** 巢狀玻璃內外圓角同心;改父 padding 內層跟著變;非 concentric 元件不受影響;硬編圓角已改 token。

**風險:** 低。

---

## B6 · Regular / Clear 兩材質(modifier class)

**API:** `lg--clear` / `lg--regular`(與 `lg-btn--pill`、`lg-btn--accent` 等 modifier 風格一致)。

**預設:** **現狀玻璃 = Clear**(refraction 1.25 / blur 1.6 / saturate 1.55),不動現有觀感;`lg--clear` 等同預設(顯式)。新增較霧的 `lg--regular`(高 blur 低透,內容上可讀)。

**優先序(釘死):** **單元素 `data-lg-*` 屬性 > 材質 preset(class) > 全域 config**。

**做法:**
- CSS:`lg--regular` 覆寫 `--lg-blur` / `--lg-saturate` 等 token 為較霧一組。
- JS:`Glass` 讀元素 class 套對應 refraction/blur/saturate preset;但元素若帶明確 `data-lg-*`,該屬性優先。

**驗收:** 同一面板切兩 class 觀感明顯不同;`lg--regular` 在內容上可讀、`lg--clear`(預設)在圖上通透;`data-lg-refraction` 等顯式屬性仍能覆寫材質 preset。

**風險:** 低(純調參),只能 Chromium 實看對比。

---

## B1 · 捲動縮小、回捲展開(navbar + tabs)

**API:** `data-lg-shrink`(navbar / tabs 加上才啟動),監聽 **window scroll**(用共用 scroll util)。

**做法:**
- `initScrollShrink()`:訂閱共用 scroll util,依 `deltaY` 方向 + threshold(避免微抖亂跳)切 `.is-condensed` class。
- CSS 用既有 `--lg-speed` / `--lg-ease` transition 收 padding / font-size / 藥丸高度。
- navbar 目前**零 JS**,這是它第一支行為。
- **tabs 特別處理:** `is-condensed` 切換改變 tab rect → **必須重跑一次藥丸定位**。把 `initTabs` 的 pill reposition 抽成可呼叫函式。**重定位掛在 padding 的 `transitionend` 觸發**(不在 class 切換當下量,否則量到 transition 半途的 rect、藥丸定位錯)。
- `prefers-reduced-motion`:定在展開態,不隨捲動變化。

**驗收:** 下捲縮小、上捲展開;捲動微抖不亂跳;tabs 縮小後藥丸仍對準 active tab;reduced-motion 定態;非 Chromium 仍正常(只是磨砂)。

**風險:** 中(方向抖動門檻要調)。

---

## B5 · Scroll edge effect(漸層遮罩 mask)

**API:** `data-lg-scroll-edge="top|bottom|both"`(上/下緣可分別開關)。

**做法:**
- **直接在捲動容器本身套 `mask-image`(`-webkit-mask` 並列)線性漸層。** mask 相對容器 box 定位、**不隨內容捲動**——這正是「捲動邊緣淡出」的標準作法,不需 sticky 覆蓋層或偽元素(那會跟著內容捲走或徒增結構)。
- 漸層 stops 依捲動位置**動態調整**:到頂 → 頂部漸層收為實心(不淡出頂緣);到底 → 底部同理。用共用 scroll util 每幀更新。
- `top` / `bottom` / `both` 控制哪一緣參與漸層;各自獨立生效。

**驗收:** 內容捲到 bar 下方淡出無硬邊;`top` / `bottom` 各自獨立;到頂/到底時對應漸隱關閉;漸隱層不隨內容捲動。

**風險:** 中(動態漸層 stops 與捲動同步的順滑度)。

---

## B3 · 按鈕 morph 成它開出的對話框(modal + 通用 helper)

**API:** 通用 `morphFrom(originEl, targetPanel)` helper;modal 開啟先套用(`data-lg-open` 觸發時傳入觸發按鈕 rect)。將來 backlog #21 Dropdown menu 可直接重用。

**做法(FLIP):**
- 開啟:記觸發按鈕 rect → `panel.animate()` 從「按鈕位置+尺寸」補間到「面板位置+尺寸」。
- 關閉:反向補間回按鈕。
- **降級:** 保留既有「液滴落地」keyframe 作為**無 origin rect 時的 fallback**;morph 是有 origin 時的主路徑。
- **兩條路徑互斥(避免 WAAPI 與 keyframe 打架):** 有 origin → 走 `panel.animate()`、**不加** keyframe class;無 origin → 加 keyframe class、不跑 WAAPI。同一 panel 任一時刻只有一條動畫。

**折射:** **全程保留折射**(使用者選定)。
⚠️ **風險標註:** Chromium 對縮放中的 `backdrop-filter: url(#svg)` 折射合成不一定穩(可能抽圓角/變形)。先實作全程保留版;**若實機證實不穩**,回報使用者,fallback 為「補間期間暫關折射、落定再開」(reviveGlass 思路)。

**驗收:** 點按鈕→面板從按鈕長出來;關閉收回按鈕;無觸發 rect 時降級回液滴動畫;reduced-motion 走簡化或即時顯示;Chromium 實機確認折射在 morph 中可接受。

**風險:** 高。

---

## 每項固定收尾流程

1. 行為/樣式改好。
2. `python3 build_site.py` 重生 `index.html`(圖示完整性需通過)。
3. `site.src.html` 對應分頁加實機展示;CLAUDE.md AI 規格書 + AI Guide 分頁補段落。
4. chrome-devtools 開 `index.html` 在 Chromium 實看(折射 + 非 Chromium 磨砂降級兩條都顧),截圖自驗。
5. 交使用者檢查 → 核可 → 動下一項。
