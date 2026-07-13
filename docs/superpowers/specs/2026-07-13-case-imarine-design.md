# iMarine 實戰案例收錄（Patterns 層）— 設計文件

日期：2026-07-13
狀態：已與使用者定案（brainstorm 兩輪 + 業界研究一輪）
範圍：UI-ToolBox repo（本 repo）；iMarine-FrontEnd repo 零改動

---

## 1. 動機與定位

UI-ToolBox 的文件現況是「元件層」齊全（18 元件 + README 的 AI 使用規格），但缺「patterns 層」——元件如何組合成完整頁面、深色主題怎麼調、多模組產品的識別色怎麼管。iMarine-FrontEnd（2026 航港大數據創意應用競賽前端，9 screens，全部用本 Kit 拼、零自訂玻璃 CSS）是目前最完整的實戰作品，把它蒸餾成案例文件，讓之後的人或 AI 用這個 Kit 時有可模仿的參照。

**定位語言借 Material Design 的三層框架**：foundations（tokens、色彩）→ components（元件）→ patterns / canonical layouts（元件組合成版面）。本輪補的是 foundations 實戰 + 一個 canonical layout：

- iMarine 的「主視覺 ~62% + 右欄卡」即 Material 三大 canonical layout 之一的 **supporting pane**，文件直接用此語彙，AI 具備的 Material 知識能直接對上。
- 四組 pattern：深色 tokens、模組色相、背景層（三者屬 foundations 實戰）、頁面節奏（canonical layout）。

**業界研究依據**（2026-07-13 調研）：

| 標竿 | 借鑑 |
| --- | --- |
| shadcn/ui | `llms.txt` 索引、規則旁附可複製實碼（open code）、「組合規則」句式 |
| Carbon / Atlassian | 每 pattern 固定四件套：anatomy 標註圖、When to use / NOT、Do/Don't 成對、token 表；開頭先講解決什麼問題 |
| Material 3 | patterns / canonical layouts 層的存在本身；supporting pane 命名 |
| llmstxt.org 規範 | `llms.txt` 結構：H1 + blockquote + H2 連結清單 + Optional 節 |
| AGENTS.md（Linux Foundation 標準，28+ 工具原生讀） | 30-50 行最有效、>150 行報酬遞減 → §5 補充規格與 AGENTS.md 都嚴控篇幅 |

## 2. 需求定案（brainstorm 問答紀錄）

1. **形態**：案例研究文件頁（非可跑範例、非只加 README 截圖）。
2. **讀者**：AI 優先、人也能讀——規則先行、可執行條列、可複製代碼，敘事為輔。
3. **內容範圍**：四組 pattern 全收（深色 tokens / 頁面節奏 / 模組色相 / 背景層與 scrim）。
4. **位置**：`docs/` 案例文件 + README 導引 + CLAUDE.md 一句話；不動展示站。
5. **公開性**：UI-ToolBox 為公開 repo，使用者確認真實截圖與競賽名稱可公開。
6. **加碼（研究後定案）**：根目錄補 `llms.txt` 與 `AGENTS.md`（~40 行精簡版）。

## 3. 產出物清單

| # | 產出 | 位置 | 說明 |
| --- | --- | --- | --- |
| 1 | 案例文件 | `docs/case-imarine.md` | 主文件，結構見 §4 |
| 2 | 截圖 6 張 | `docs/case-imarine/*.webp` | 2 張帶 anatomy 標註，見 §6 |
| 3 | llms.txt | repo 根 | llmstxt.org 規範，~20 行，見 §5 |
| 4 | AGENTS.md | repo 根 | ~40 行，給外部 agent；與 CLAUDE.md 分工，見 §5 |
| 5 | README 導引 | `README.md` | 「用這套能做出什麼」之後加「實戰案例」節：1 張代表圖 + 兩句話 + 連結 |
| 6 | CLAUDE.md 一句話 | `CLAUDE.md` | 「遇深色/儀表板/多模組需求，先讀 `docs/case-imarine.md`」 |

## 4. `docs/case-imarine.md` 逐節設計

寫法通則（每個 pattern 節的固定結構，Carbon 四件套）：

```
這解決什麼問題（一句 why）
When to use / When NOT to use
規則（Do/Don't 成對條列，可執行句式）
可複製代碼（token :root 區塊 / HTML 骨架 / CSS 區塊）
截圖佐證（其中 §2、§3 為 anatomy 標註圖）
```

截圖只是佐證：拿掉所有圖，文件仍自足（AI 多半只讀文字）。

### 開場（~15 行）

這是什麼（2026 航港競賽前端、9 screens、深色 Liquid Glass、Vite + vanilla TS shell、全部用 Kit 的 class 拼、零自訂玻璃 CSS）→ 本文件教什麼（四個可複製 pattern + 一份可貼 AI 的補充規格）→ hero 總覽圖一張。

### §1 深色主題 tokens 系統（foundations）

- Why：Kit 預設語境偏亮色背景；深色下的文字梯度、髮絲線、發光參數需要一套已驗證的值。
- When to use：暗場景儀表板、監控台、簡報 demo。When NOT：內容閱讀型長文頁。
- 規則例：文字梯度一律用 ink 四階（.92/.62/.5/.4 的 `rgba(255,255,255,x)`），Don't 用任意灰；分隔線一律 `--hair`，Don't 用實色灰線；動畫緩動一律 `--ease`。
- 可複製代碼：完整 `:root` 區塊，**值一律從 iMarine `src/ui/tokens.css` 實碼抽取**（含 `--lg-accent:#35E0A6`、`--bg:#070b11`、gold/cyan/amber/rose/flame、ink 四階、`--hair`、`--ease:cubic-bezier(.22,1,.36,1)`、`--mono` 與 Inter/Noto Sans TC 字體堆疊）——不是 CLAUDE.md 摘要的簡表。附 `<html data-lg-theme="dark">` 與 Kit 銜接說明。

### §2 儀表板頁面節奏（canonical layout：supporting pane 變體）

- Why：一頁儀表板該怎麼從上到下組織，讓多頁產品每頁節奏一致。
- 公式：eyebrow 標頭 → 標題列（技術徽章 + 資料源 chip）→ KPI 統計列 → 主視覺（~62%）+ 右欄卡 → stagger 進場。
- 規則例：進場 stagger 用 `.anim` + `style="--d:.14s"` 遞增 delay（實碼慣例）；KPI 卡遵守「玻璃容器 + 實心內容」鐵則（數字、sparkline 不透明）；小型/大量重複元件用 `lg-static`。
- 可複製代碼：~60 行頁面 HTML 骨架，全用 `.lg` class + `data-lg`，自 dispatch 頁實碼簡化（保留結構、拔除業務 id）。
- Anatomy 標註圖：dispatch 全頁截圖，框註五部位（eyebrow / 標題列 / KPI 列 / 主視覺 62% / 右欄卡）。

### §3 模組輔助色相系統（foundations：多模組識別色紀律）

- Why：多模組產品需要識別色，但玻璃介面大面積上彩色會毀掉材質感。
- 核心機制：`--mc` custom property 注入——元件樣式寫一次（如 `.rbtn.on{background:color-mix(in srgb,var(--mc) 20%,transparent)}`），換模組只換一個變數，零樣式分支。
- 規則：色相只准出現在三個位置（rail active、eyebrow 圓點、徽章）；Don't 拿色相當卡片底色或大面積填色；主行動色永遠 `--lg-accent`。
- 附表：七色相（carbon 金 `#E9BC63` / policy 青 `#38BDF8` / twin 藍 `#7FB4FF` / dispatch 琥珀 `#F5A54A` / epidemic 玫紅 `#F0648C` / alert 橘紅 `#FF7A59` / agent 紫 `#B48CFF`）。
- Anatomy 標註圖：rail + eyebrow 合成截圖，圈註三個合法位置。

### §4 背景層與 scrim 兩態（foundations：玻璃的舞台）

- Why：Kit 鐵則 3「頁面必須有多彩背景」的實戰放大——背景怎麼給、怎麼壓才不搶內容。
- 結構：z-index 分層圖解（文字版即可）：`#harbor` 點雲 → glowfx 光暈 → `#veil` → `#backdrop` 影片 → `#backdrop-scrim` → 內容層。單一 `<video>` 集中層，全站共用。
- 兩態：空間型頁背景亮、文件型頁 scrim 壓暗；由 `data-mode`（cover/ov/doc）驅動三組 scrim 漸層值（抄實碼：cover 起頭 .5 / ov .72 / doc .86）。
- 規則例：影片永遠 `brightness(.75)` + `opacity:.8` 退為氛圍；reduced-motion 退 poster 靜態幀；scrim 純 CSS 切態、不用 JS 算。
- 可複製代碼：backdrop + scrim 完整 CSS 區塊（自 `tokens.css` 實碼抽取）。

### §5 貼給 AI 的補充規格（嚴控 ≤50 行）

- 濃縮 §1-4 成 README「AI 使用規格」同格式的純文字 code block，開頭一句「以下接在 Liquid Glass Kit 主規格之後使用」。
- 內含：`:root` tokens 精簡版、頁面節奏五步公式、色相三位置紀律、背景 + scrim 最小實作。
- 篇幅依據 AGENTS.md 研究：30-50 行最有效——寧可砍細節、留規則。

### §6 變更紀錄

一行表：日期、對應 iMarine commit hash、摘要。日後兩邊漂移可考。

## 5. `llms.txt` 與 `AGENTS.md`

**`llms.txt`**（~20 行，llmstxt.org 規範：H1 + blockquote + H2 連結清單 + Optional）：

```
# Liquid Glass Kit
> 零依賴液態玻璃 UI 工具包：18 元件、Snell 定律即時折射、為 AI 協作而生。

## 核心
- [AI 使用規格](README.md)：貼給 AI 的元件規格書（README 內含一鍵複製全文）
- [liquid-glass.css](liquid-glass.css)：工具包樣式
- [liquid-glass.js](liquid-glass.js)：工具包引擎

## 實戰 Patterns
- [iMarine 深色儀表板案例](docs/case-imarine.md)：深色 tokens／頁面節奏／模組色相／背景層與 scrim

## Optional
- [CLAUDE.md](CLAUDE.md)：repo 內開發規則（維護者用）
```

（實作時依實際錨點與檔名微調；上述為形狀示意。）

**`AGENTS.md`**（~40 行；研究顯示 30-50 行最有效）與 CLAUDE.md 分工：

- CLAUDE.md = 給「維護此 repo」的 agent：建置流程、site.src.html 鐵律、icons.json 規則。
- AGENTS.md = 給「使用此 Kit」的外部 agent：專案一句話、六條鐵則摘錄、主規格書在 README、深色/儀表板/多模組需求先讀 `docs/case-imarine.md`、不要手寫 backdrop-filter。
- AGENTS.md 開頭一句註明分工（「維護本 repo 請改讀 CLAUDE.md」），避免四入口（README/CLAUDE.md/llms.txt/AGENTS.md）語意重疊漂移；llms.txt 與 AGENTS.md 都只做「指路」，內容單一真相仍在 README 與案例文件。

## 6. 截圖規格

| 圖 | 內容 | 標註 | 用於 |
| --- | --- | --- | --- |
| hero 總覽 | 開場代表圖 | 無 | 開場 + README 實戰案例節 |
| dispatch 全頁 | 頁面節奏標準樣板 | 有：五部位框線 + 名稱 | §2 anatomy |
| rail + eyebrow 合成 | 色相三合法位置 | 有：三圈註 | §3 anatomy |
| carbon（doc 態） | scrim 壓暗對照 | 無 | §4 |
| twin（空間態） | 背景亮對照 | 無 | §4 |
| hero 封面 | 影片背景 + 輕 scrim | 無 | §4 |

拍攝管線：Playwright headless 對 iMarine 自起的獨立 dev server（`--strictPort`、跑畢清 port、不動使用者既有服務與 `.env`）。標註方式：Playwright 於截圖前注入 HTML 疊層（框線 + 標籤）再截，同一管線完成、不需事後影像加工。輸出 webp，單張 < 300KB（比照既有 `docs/*.webp`）。截圖畫面不得入鏡任何 key、後端位址等敏感資訊。

## 7. 驗收標準

1. **AI 盲測**：乾淨 session 的 AI 只給「README 主規格 + §5 補充規格」兩段文字，指令「做一個深色三模組監控儀表板」，產出需命中四點：深底非純黑（用 `--bg` 色系）、有 KPI 統計列、模組色相只出現在合法位置、有多彩背景 + scrim。
2. **token 保真**：文件內每個 CSS 值與 iMarine `src/ui/tokens.css` 實碼逐字一致；§6 變更紀錄記下比對當下的 iMarine commit hash。
3. **llms.txt 合規**：H1 + blockquote + H2 連結清單結構；所有連結（llms.txt、AGENTS.md、README、CLAUDE.md、案例文件內部）逐一有效。
4. **零回歸**：`liquid-glass.css`、`liquid-glass.js`、`index.html`、`site.src.html`、既有 `docs/*.webp` 全部零 diff。
5. **iMarine 零改動**：iMarine repo 全程唯讀（起 dev server 拍圖不算改動）。
6. **篇幅紀律**：§5 補充規格 ≤ 50 行；AGENTS.md ≤ 50 行。

## 8. 邊界（不做的事）

- 不動展示站（`site.src.html` / `index.html` / `build_site.py`），不改 Kit 本體兩檔。
- 不搬任何可執行程式碼進 UI-ToolBox；iMarine 的 TS 邏輯不降解成 vanilla、不維護第二份實作。
- iMarine repo 零改動。
- 不做 MCP server / skills 式主動注入機制（shadcn 等級工程）；llms.txt + AGENTS.md 已滿足「被動可發現」，真有需求日後另案。
- 文件不寫死 iMarine 的業務內容（AIS、碳權流程等）——只蒸餾視覺 pattern，業務名詞僅出現在開場定位與截圖裡。

## 9. 風險與緩解

| 風險 | 緩解 |
| --- | --- |
| 兩 repo 漂移（iMarine tokens 日後改值） | §6 變更紀錄記 commit hash；案例文件定位為「快照 + 紀律」，紀律不隨值漂移 |
| 文件入口過多語意重疊 | llms.txt / AGENTS.md 只指路不承載內容；單一真相在 README 與案例文件 |
| AI 盲測不過 | 回頭修 §5 規格的措辭（規則句式化），不加長篇幅 |
