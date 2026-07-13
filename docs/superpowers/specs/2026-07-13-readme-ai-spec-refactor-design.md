# README 重構 + SPEC.md 單一真相 — 設計文件

日期:2026-07-13
狀態:已與使用者逐節確認(§1–§4 全數核可)

## 動機與問題

目標:讓 Kit 順利與 AI 協作開發,**主要情境是 AI agent 直接讀 repo**(使用者把 Kit 放進專案,Claude Code / Cursor 等 agent 自行讀文件拼介面),人類複製規格書貼給對話式 AI 為次要路徑。

現況問題:

1. **規格書有三個副本且其一過時**:CLAUDE.md(最新)、site.src.html 約 line 2029 的 JS 字串(最新)、README `<details>` 內嵌(**過時**——停在 18 件元件,缺表單家族 8 件、材質變體 `lg--clear/--regular`、morph 對話框、`data-lg-concentric/-shrink/-scroll-edge`)。
2. AGENTS.md 與 llms.txt 都宣告「元件規格單一真相 = README 的 AI 使用規格」——單一真相指向唯一過時的那份。
3. 規格書是「一行一元件」的密集純文字塊,為貼進對話而優化;作為 agent 直讀檔案,結構化 Markdown 更好解析、好讀、好 diff。

## 決策紀錄(與使用者逐題確認)

| 議題 | 決定 |
| --- | --- |
| 主要情境 | AI agent 直接讀 repo |
| 單一真相 | 新增獨立 `SPEC.md`(根目錄)+ build 注入展示站;其餘檔案改指路 |
| README 定位 | 精簡人類入口,刪內嵌規格全文 |
| 規格書重寫幅度 | 結構化 Markdown(內容等價、不增減功能敘述) |
| 元件家族截圖更新 | 範圍外(之後另行處理) |

## §1 架構:單一真相與流向

新增根目錄 **`SPEC.md`** 作為元件規格書唯一真相。選根目錄(非 docs/)因 agent 掃 repo 時根目錄最易發現,與 AGENTS.md、llms.txt 同層。

```
SPEC.md(唯一真相,agent 直讀)
  ├─ build_site.py ─讀取注入→ site.src.html 的 {{AI_SPEC}} 佔位符 → index.html AI 分頁
  ├─ README.md   → 一行指路 + 連結(不再內嵌全文)
  ├─ AGENTS.md   → 「元件規格單一真相 = SPEC.md」
  ├─ llms.txt    → 核心索引第一條列 SPEC.md
  └─ CLAUDE.md   → 移除內嵌全文,改指路 + 鐵律「改元件時規格只改 SPEC.md」
```

- `site.src.html` 內嵌規格 JS 字串改為 `{{AI_SPEC}}` 佔位符,由 build_site.py 讀 SPEC.md 注入——與 `{{CSS}}`/`{{JS}}` 同機制。
- SPEC.md 不存在時 build 直接失敗(fail-fast,同缺圖示)。
- README 的過時副本直接刪除,不搬救。

## §2 SPEC.md 內容

以 site.src.html / CLAUDE.md 的最新版規格為內容基準(26 件元件:原 18 件 + 表單家族 8 件),**重寫為結構化 Markdown,內容等價、不增減功能敘述**:

- 每元件一小節:HTML 範例用 fenced code block,行為要點與狀態用清單。
- 屬性(data-lg-*)與 JS API 用表格。
- 章節骨架沿用現有順序:初始化 → 鐵則 → 元件結構 → 屬性 → JS API → 材質變體 → Tokens。
- 開頭加宣告:「本檔是元件規格的單一真相;修改元件時同步更新此檔」。
- 結尾加 patterns 層指路:「深色主題/儀表板/多模組介面 → 先讀 docs/case-imarine.md,其 §5 為可接續本規格的補充規格」。

單一檔案兩用:agent 直讀,人類也可整檔複製貼給對話式 AI(Markdown 貼進對話無損失)。

## §3 README 新結構(精簡人類入口)

```
1. Hero        — 標題 + 價值主張 + hero 圖 + Chromium 降級說明(維持現有)
2. 能做出什麼   — 展示截圖節(展廳/儀表板/深色/iMarine,維持,文案微調)
3. 快速開始     — 上移(人類最想先看到的);內容維持現有
4. 🤖 與 AI 協作 — 全面改寫為指路式:
     主打 agent 直讀——把 liquid-glass.css/js + SPEC.md(+ AGENTS.md)放進專案,
     agent 自己讀規格拼介面;對話式 AI 則「複製 SPEC.md 全文貼上」。
     刪除 <details> 內嵌規格全文。
5. 元件一覽     — 保留四組截圖與 class 速覽,更新為 26 件(補表單家族),
     註明完整結構在 SPEC.md
6. 瀏覽器支援 / 授權 — 維持現有
```

附帶:全 repo「18 個元件」字樣(README、AGENTS.md、llms.txt)更新為 26 件。元件家族截圖(components-*.webp)無表單家族——**截圖更新列為範圍外待辦**,README 文字先行。

## §4 周邊檔案、build 與驗證

### 各檔改動一覽

| 檔案 | 改動 |
| --- | --- |
| `SPEC.md` | 新增:結構化 Markdown 規格(§2) |
| `build_site.py` | 讀 SPEC.md 注入 `{{AI_SPEC}}`;缺檔即 build 失敗 |
| `site.src.html` | 刪內嵌規格 JS 字串(約 line 2029 起),改 `{{AI_SPEC}}` 佔位符;AI 分頁 UI 與複製按鈕不變 |
| `README.md` | §3 新結構 |
| `AGENTS.md` | 規格真相改指 SPEC.md;元件數 26 |
| `llms.txt` | SPEC.md 列核心第一條;元件數 26 |
| `CLAUDE.md` | 刪內嵌規格節、改指路;鐵律新增「改元件時規格只改 SPEC.md 一處」 |

### 實作時須查證的技術點

1. **注入格式**:規格在 site.src.html 內是 JS 字串,build 需把 Markdown 安全轉義為 JS 字串字面量(反引號、`${`、反斜線)。與 `{{CSS}}` 同機制但多一步轉義。
2. **圖示掃描互動**:規格文含 `#ph-x`、`#ph-star-fill` 等字面引用;查證 build_site.py 的缺圖檢查掃的是 site.src.html 原始檔還是注入後產物,確保注入後不誤判、不漏判。

### 錯誤處理

- SPEC.md 缺檔 → build 失敗並明確報錯。
- `{{AI_SPEC}}` 佔位符缺失(site.src.html 被改壞)→ 依現有佔位符機制行為;若現有機制對未消耗的注入內容不報錯,實作時補上檢查。

### 驗證

- `python3 build_site.py` 成功;`index.html` 無殘留 `{{AI_SPEC}}`;含 `lg-otp` 等新元件字樣(證明注入的是新規格)。
- 瀏覽器人工確認展示站 AI 分頁顯示與一鍵複製正常(折射效果照例僅能人工目視)。
- 全 repo grep:不再出現「18 個元件」;無任何文件仍宣稱規格內嵌於 README。

## 範圍外

- 元件家族截圖(components-*.webp)補拍表單家族。
- 規格書內容的功能性增補(選型指引等)——此次僅結構化重寫,內容等價。
- index.html AI 分頁的 UI 改版。
