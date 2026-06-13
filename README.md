# Liquid Glass Kit

零依賴的液態玻璃 UI 工具包。透明玻璃材質、以 Snell 定律即時計算的液態折射與色散、發光背景、慣性拖曳,以及 18 個現成元件。複製兩個檔案即可用於任何 Web 或 App(WebView / Electron)介面,不需要任何建置工具或框架。

打開 `index.html` 即是工具包網站,分三個分頁:「首頁」是以本工具包元件組成的莫內線上展廳範例(全螢幕影片背景,失效時自動換成畫作);「元件與指引」可瀏覽 18 件元件、即時調參並複製程式碼;「AI 整合」提供給 Claude Code、Cursor、Copilot 與對話式 AI 的完整規格書與設定檔範例,讓 AI 直接用這套工具包替你開發介面。

## 運作原理

工具包對每個玻璃元素生成一張位移貼圖:沿圓角矩形邊緣取「凸超橢圓(convex squircle)」斷面,以 Snell 定律(折射率 1.5)做光線追蹤,算出光線穿過玻璃後的橫向偏移,寫入貼圖的 R(X 位移)與 G(Y 位移)通道,再透過 SVG `feDisplacementMap` 搭配 `backdrop-filter` 即時折射元素背後的真實內容。色散由 RGB 三通道以略微不同的位移倍率合成。凸面斷面讓位移永遠指向元件內部,邊緣取樣不會越界。

## 瀏覽器支援

| 環境 | 行為 |
| --- | --- |
| Chrome、Edge、Arc、Opera、Electron 等 Chromium | 完整液態折射與色散 |
| Safari、Firefox、iOS 全部瀏覽器 | 自動降級為磨砂玻璃(blur + saturate),版面與互動完全相同 |
| 系統開啟「降低透明度」 | 改用近不透明面板,停用折射與模糊 |
| 系統開啟「減少動態效果」 | 停用發光漂移、慣性與彈性動畫 |

偵測是自動的:`liquid-glass.js` 會在 `<html>` 標上 `lg-full` 或 `lg-fallback`,不需要手動處理。

## 快速開始

1. 複製 `liquid-glass.css` 與 `liquid-glass.js` 到專案。
2. 引入並初始化:

```html
<link rel="stylesheet" href="liquid-glass.css">
<script src="liquid-glass.js"></script>
<script>
  LiquidGlass.init({ refraction: 1.25, chromatic: 0.55 });
</script>
```

3. 替元素加上玻璃:

```html
<!-- 玻璃材質 + 液態折射 -->
<div class="lg lg-card" data-lg>內容</div>

<!-- 單一元素微調 -->
<div class="lg lg-card" data-lg data-lg-refraction="1.6" data-lg-chromatic="0.8">內容</div>

<!-- 輕量磨砂(不折射,適合小或大量重複的元件) -->
<span class="lg lg-static">內容</span>
```

`class="lg"` 提供材質(底色、鏡面 rim light、動態光澤、陰影);`data-lg` 啟用折射引擎。兩者通常一起使用。

## 元件

全部元件的完整 HTML 結構都在「元件與指引」分頁可直接複製(也整理在「AI 整合」分頁的元件程式碼庫),以下列出 18 件的 class 名稱:按鈕 `.lg-btn`(修飾:`--pill` `--accent` `--icon` `--lg` `--sm`)、卡片 `.lg-card`、導航列 `.lg-navbar`、搜尋框 `.lg-search`、開關 `.lg-switch`(純 CSS)、滑桿 `.lg-slider`、分頁 `.lg-tabs`、對話框 `.lg-modal`、工具提示(任何元素加 `data-lg-tip="文字"`)、Dock `.lg-dock`、標籤 `.lg-chip`、徽章 `.lg-badge`、拖曳面板(任何元素加 `data-lg-drag`)、統計卡 `.lg-stat`、進度條 `.lg-meter`、環形儀表 `.lg-gauge`、圖表 `.lg-chart`、通知(以 `LiquidGlass.toast({ title, message, icon })` 呼叫)。

發光背景容器:

```html
<div class="lg-glow" style="--lg-glow-base:#7d92ad;">
  <div class="lg-glow__image" style="--lg-bg-image:url('bg.jpg');"></div>
  <!-- 其上的內容 -->
</div>
```

## JavaScript API

| 方法 / 屬性 | 說明 |
| --- | --- |
| `LiquidGlass.init(config?)` | 偵測能力、套用全域設定、掃描 `data-lg` 等屬性並啟動所有元件行為。整頁呼叫一次。 |
| `LiquidGlass.attach(el, opts?)` | 手動替元素掛上折射(動態插入的節點用)。回傳實例,含 `update()` `setOptions(opts)` `destroy()`。 |
| `LiquidGlass.draggable(el, opts?)` | 啟用拖曳。`opts = { handle, bounds: 'viewport' | 'parent', inertia: true }`。回傳 `{ destroy() }`。 |
| `LiquidGlass.refresh()` | 全域設定改變後,同步更新所有實例(只改濾鏡倍率,不重算貼圖,代價極低)。 |
| `LiquidGlass.config` | 全域設定物件,見下表。 |
| `LiquidGlass.supported` | 是否為完整折射模式。 |
| `LiquidGlass.behaviors` | `{ tabs, slider, dock }`,供動態插入的元件手動初始化。 |

### 全域設定(`LiquidGlass.config` / `init()` 參數)

| 鍵 | 預設 | 說明 |
| --- | --- | --- |
| `refraction` | `1.25` | 折射強度倍率,1 為物理值 |
| `chromatic` | `0.55` | 色散強度 0–1 |
| `blur` | `1.6` | 玻璃內霧化 px |
| `saturate` | `1.55` | 透過玻璃的飽和度 |
| `bezel` | `0.16` | 邊緣斜面寬,佔短邊比例 |
| `bezelMin` / `bezelMax` | `10` / `42` | 斜面 px 上下限 |
| `thickness` | `28` | 玻璃厚度 px |
| `profile` | `'squircle'` | 斷面:`squircle` `circle` `lip` |
| `ior` | `1.5` | 折射率 |
| `maxWidth` | `900` | 超過此寬度自動減弱折射,保護 GPU |

### HTML 屬性

| 屬性 | 說明 |
| --- | --- |
| `data-lg` | 啟用折射 |
| `data-lg-refraction` `data-lg-chromatic` `data-lg-blur` `data-lg-saturate` `data-lg-bezel` `data-lg-thickness` `data-lg-profile` | 覆寫單一元素的對應設定(bezel、thickness 為 px) |
| `data-lg-drag="viewport \| parent"` | 啟用拖曳與邊界 |
| `data-lg-drag-handle=".selector"` | 指定拖曳把手 |
| `data-lg-tip="文字"` | 工具提示 |
| `data-lg-open="#modalId"` / `data-lg-close` | 開關對話框 |
| `data-lg-theme="dark"`(加在 `<html>`) | 手動切換暗色;不加則跟隨系統 |

## CSS Tokens

所有顏色與節奏都可在 `:root` 覆寫。常用的有:`--lg-tint`(玻璃底色)、`--lg-accent`(強調色,預設為莫內畫中胸花的珊瑚紅 `#cf6045`,換成品牌色即可整體換膚)、`--lg-text` / `--lg-text-dim`、`--lg-radius-s/m/l/pill`、`--lg-shadow`、`--lg-ease`(液態回彈曲線)、`--lg-blur-fallback`(降級模糊量)、`--lg-font`。完整清單見 `liquid-glass.css` 第一節。

## 效能準則

折射的成本與面積成正比。給大面板留給真正重要的層;小而大量重複的元件(列表項、標籤)用 `.lg-static` 磨砂即可。寬度超過 `maxWidth`(預設 900px)的元素會自動減弱折射。位移貼圖會以尺寸為鍵快取,同尺寸的按鈕共用同一張貼圖;調整 `refraction` `chromatic` `blur` `saturate` 不會觸發貼圖重算。

## 無障礙

所有互動元件具備鍵盤焦點樣式(`:focus-visible`)、分頁支援方向鍵、對話框支援 Esc 關閉並歸還焦點、開關以原生 checkbox 實作。`prefers-reduced-transparency` 與 `prefers-reduced-motion` 皆有對應降級。玻璃上的文字請維持足夠對比——必要時提高該元素的 `--lg-tint` 不透明度。

## 設計準則

玻璃是控制層,內容才是主角。只把玻璃用在漂浮於內容之上的導航、工具列、面板與對話框;內容本身(文章、圖片、表格)不上玻璃。層級靠深度與折射傳達:愈靠近使用者的層,玻璃感愈明確。克制使用——整個畫面只有少數幾片玻璃時,材質才珍貴。

## AI 開發工具整合

`index.html` 的「AI 整合」分頁內含一份可一鍵複製的 AI 規格書(濃縮全部元件結構、屬性與鐵則)。把它存成專案根目錄的 `CLAUDE.md`(Claude Code)、`.cursor/rules/liquid-glass.mdc`(Cursor)或 `.github/copilot-instructions.md`(GitHub Copilot),AI 之後就會以工具包的 class 與 API 實作介面,而不是自己手寫 backdrop-filter;對話式 AI 則直接貼上規格書加任務描述即可。

## 授權與素材

程式碼可自由用於個人與商業專案。網站圖示來自 Phosphor Icons(MIT License);畫作為 Claude Monet《向日葵花束》(1881)、《睡蓮池上的橋》(1899)與《撐陽傘的女人(面向左)》(1886),均為公有領域。

## v0.1 — 液態物理

工具包現在內建四種液態行為,引入即生效、零設定:

1. **擠壓回彈** — 按鈕、chip、分頁籤、Dock 圖示與任何標上 `data-lg-press` 的元素,按下時被彈簧壓扁、放開後欠阻尼回彈;有折射的玻璃同步「鼓起」(位移貼圖即時放大,零重算)。
2. **拖曳拉伸** — `data-lg-drag` 元素拖動時沿速度方向拉伸(體積守恆),釋放後慣性滑行並以果凍抖動收斂。
3. **黏滯融合(goo)** — Dock 底部的游標液滴會與圖示液滴融合、分離;開關切換時錨點液滴被拉斷、在另一端重聚(SVG blur + alpha 對比濾鏡,只作用於色塊層,與折射層無衝突)。
4. **液滴遷移** — 分頁膠囊切換時途中拉長、抵達擠壓;對話框出場為液滴落地回彈。

公開 API:`LiquidGlass.Spring(value, { stiffness, damping, onUpdate, onRest })` 可用於自訂彈簧動畫;`glass.setBulge(k)` 即時縮放折射強度。`prefers-reduced-motion` 下全部物理自動降級。
