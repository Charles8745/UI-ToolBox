# Liquid Glass Kit — Agent 指引

> 給「使用本 Kit 開發介面」的 AI agent。要維護本 repo（改 Kit 本體或展示站）請改讀 CLAUDE.md。

## 這是什麼

零依賴液態玻璃 UI 工具包：liquid-glass.css + liquid-glass.js 兩檔即可用，18 個現成元件。
折射僅 Chromium 完整支援，其他瀏覽器自動降級為磨砂玻璃，版面與互動不變。

## 開始之前

- 元件規格單一真相：README 的「AI 使用規格」（含一鍵複製全文），先讀再動手。
- 深色主題 / 儀表板 / 多模組產品需求：先讀 docs/case-imarine.md
  （實戰 patterns：深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim），
  其 §5 是可直接接在主規格之後使用的補充規格。

## 鐵則（違反即錯）

1. 玻璃只用於浮在內容之上的控制層（導航、卡片、面板、對話框、dock）；內容本身不上玻璃。
2. 折射玻璃 = class="lg" + data-lg；小型或大量重複的元件改用 class="lg lg-static"。
3. 頁面必須有圖像或多彩背景，玻璃效果才看得見。
4. 不要手寫 backdrop-filter 或自製玻璃 CSS，一律用工具包的 class 與 API。
5. 動態插入的節點呼叫 LiquidGlass.attach(el)。
6. 儀表元件 = 玻璃容器 + 實心內容層：數字、走勢圖、圖表本身不透明。

## 快速起手

    <link rel="stylesheet" href="liquid-glass.css">
    <script src="liquid-glass.js"></script>
    <script>LiquidGlass.init();</script>

## 文件地圖

- README.md：人類入口 + AI 使用規格全文
- docs/case-imarine.md：深色儀表板實戰案例（patterns 層）
- llms.txt：機器可讀索引
- CLAUDE.md：維護者專用（建置流程與鐵律）
