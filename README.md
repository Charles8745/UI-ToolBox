# Liquid Glass Kit

> 零依賴的「液態玻璃」UI 工具包 —— 26 個現成元件、以 Snell 定律即時計算的折射與色散、發光背景、慣性拖曳。複製兩個檔案(`liquid-glass.css` + `liquid-glass.js`)就能用,不需建置工具、不需框架。**而且特別為「與 AI 協作開發」而設計**:元件規格單一真相 [SPEC.md](SPEC.md),AI agent 讀了就會用這套元件替你拼介面。

![Liquid Glass Kit hero](docs/hero.webp)

> 折射僅 Chromium 引擎(Chrome / Edge / Arc / Electron…)完整支援,其他瀏覽器**自動降級為磨砂玻璃**,版面與互動完全不變。

---

## 用這套能做出什麼

下面全部是 `index.html` 的實際畫面 —— **每一片玻璃、每一個圖表都是工具包的 class 拼出來的,沒有一行自訂玻璃 CSS**。

**內容展廳 / 作品集** — 玻璃導覽列、Dock、搜尋、篩選分頁與卡片漂浮在畫作之上:

![內容展廳](docs/gallery.webp)

**分析儀表板** — 統計卡、折線圖、環形儀表、進度條;改一個 `data-lg-value` 屬性,數字與弧線就以彈簧一起跳動:

![分析儀表板](docs/dashboard.webp)

**深色主題** — 同一套元件,`<html data-lg-theme="dark">` 一鍵換膚:

![深色主題](docs/dark-theme.webp)

**實戰案例 — 永續智能航港生態系(iMarine)** — 9 個 screen 的深色儀表板全站,從封面到六大功能頁全部用 Kit 的 class 拼出,零自訂玻璃 CSS:

![iMarine 戰情總覽](docs/case-imarine/hero-overview.webp)

> 深色 tokens、頁面節奏、模組識別色紀律、背景層與 scrim 的完整拆解,以及一份可直接貼給 AI 的「深色儀表板補充規格」,見 **[docs/case-imarine.md](docs/case-imarine.md)**。

---

## 快速開始

```html
<link rel="stylesheet" href="liquid-glass.css">
<script src="liquid-glass.js"></script>
<script>LiquidGlass.init();</script>

<!-- 玻璃材質 + 即時折射 -->
<div class="lg lg-card" data-lg>內容</div>

<!-- 輕量磨砂(不折射,適合小或大量重複的元件) -->
<span class="lg lg-static">內容</span>
```

`class="lg"` 提供材質,`data-lg` 啟用折射,通常一起用;動態插入的節點呼叫 `LiquidGlass.attach(el)`。頁面要有圖像或多彩背景,玻璃才看得見(可用 `.lg-glow` 容器)。完整的元件結構、屬性與 JS API 都在 **[SPEC.md](SPEC.md)**。

---

## 🤖 與 AI 協作開發

這套工具包**為 AI 協作而生**:元件是固定的 class 與 API,規則濃縮成單一真相 **[SPEC.md](SPEC.md)**(鐵則、26 件元件結構、屬性、JS API、材質與 tokens),AI 不必(也不該)自己手刻 `backdrop-filter`。

**AI agent(Claude Code、Cursor、Copilot 等)——推薦用法:**

把 `liquid-glass.css`、`liquid-glass.js`、`SPEC.md` 複製進你的專案(建議連 [AGENTS.md](AGENTS.md) 一起),然後直接交代任務,例如:

> 用 Liquid Glass Kit 做一個帶導覽列與三張統計卡的儀表板

agent 會自己讀 SPEC.md,用 `.lg` class 與 `LiquidGlass` API 實作,而不是自己亂寫玻璃樣式。

**對話式 AI(ChatGPT / Claude.ai 等):**

複製 [SPEC.md](SPEC.md) 全文貼進對話,後面接上你的任務描述。

**深色主題 / 儀表板 / 多模組介面:**

讓 AI 再讀 [docs/case-imarine.md](docs/case-imarine.md)(patterns 層:深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim),其 §5 是可直接接在 SPEC 之後的補充規格。

> `index.html` 的「AI 整合」分頁內也有同一份規格書的一鍵複製按鈕與各工具設定範例。

---

## 元件一覽

26 件元件,分五組。完整 HTML 結構在 [SPEC.md](SPEC.md),也能在 `index.html` 的「元件與指引」分頁即時調參、一鍵複製。

**基礎** — 按鈕 `.lg-btn`(修飾 `--pill` `--accent` `--icon` `--lg` `--sm`)、圖示按鈕 `.lg-btn--icon`、卡片 `.lg-card`。按下有彈簧擠壓回彈。

![基礎元件:按鈕、圖示按鈕、卡片](docs/components-core.webp)

**控制** — 開關 `.lg-switch`(純 CSS)、滑桿 `.lg-slider`、分頁 `.lg-tabs`(膠囊液態遷移)、搜尋框 `.lg-search`。

![控制元件:開關、滑桿、分頁、搜尋](docs/components-controls.webp)

**表單** — 文字輸入 `.lg-field`(浮動標籤)、多行輸入 `.lg-field--area`、核取方塊 `.lg-check`、單選 `.lg-radio`、步進器 `.lg-stepper`、星等評分 `.lg-rating`、驗證碼 `.lg-otp`、檔案上傳 `.lg-upload`(拖放)。

**導覽與互動** — 導覽列 `.lg-navbar`、Dock `.lg-dock`(游標鄰近放大)、拖曳 `data-lg-drag`(慣性 + 拉伸)、工具提示 `data-lg-tip`、對話框 `.lg-modal`(從觸發按鈕 morph 長出)、標籤 `.lg-chip` · 徽章 `.lg-badge`。

![導覽元件:導覽列、Dock、拖曳](docs/components-nav.webp)

**資料視覺化** — 統計卡 `.lg-stat`、進度條 `.lg-meter`、環形儀表 `.lg-gauge`、圖表 `.lg-chart`、通知 `LiquidGlass.toast()`。全部「屬性驅動」:改 `data-lg-value` / `-spark` / `-points` 即觸發彈簧動畫。

![資料元件:統計卡、進度條、環形儀表、圖表](docs/components-data.webp)

> 這幾件是「玻璃容器 + 實心內容層」:外框是玻璃,但數字、走勢圖、圖表本身不透明——內容上玻璃會看不見,這是技術上必要的邊界。

---

## 瀏覽器支援

| 環境 | 行為 |
| --- | --- |
| Chrome / Edge / Arc / Opera / Electron 等 Chromium | 完整液態折射與色散 |
| Safari / Firefox / iOS 全部瀏覽器 | 自動降級為磨砂玻璃,版面與互動完全相同 |
| 系統「降低透明度 / 減少動態」 | 自動停用折射 / 動畫 |

偵測是自動的,不需手動處理。

## 授權與素材

程式碼可自由用於個人與商業專案。圖示來自 Phosphor Icons(MIT License);畫作為 Claude Monet《向日葵花束》(1881)、《睡蓮池上的橋》(1899)與《撐陽傘的女人(面向左)》(1886),均為公有領域。
