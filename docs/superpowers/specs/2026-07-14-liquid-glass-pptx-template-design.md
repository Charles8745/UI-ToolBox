# Liquid Glass PowerPoint 模板（presentation/ 子專案）設計文件

日期：2026-07-14
狀態：已與 owner 逐節確認通過

---

## 1. 目標與定位

做一份**真正的 PowerPoint 模板檔（.pptx）**，視覺與 Liquid Glass Kit 完全同源：使用者在 PowerPoint 裡直接打字、搬卡、新增頁面，不需要碰任何程式。

- **歸屬**：UI-ToolBox 的官方 presentation template（新子專案 `presentation/`），通用產品，不綁單一專案。
- **第一個使用者**：iMarine（2026 航港大數據創意應用競賽）簡報。
- **主題**：先做深色一套（iMarine 語彙：底 `#070b11` + 霓虹 accent）。管線全程參數化（tokens 進、產物出），未來加淡色 Monet 主題 = 換 tokens 重跑。
- **非目標**：HTML 簡報播放器、reveal.js/Slidev 整合、PDF 匯出工具——本專案的產物就是 .pptx 本身。

## 2. 技術事實依據（決策的根據，勿重查）

1. **PowerPoint 沒有 backdrop blur**：無法即時模糊下層內容。所有「PPT 玻璃」教學都是預先模糊背景圖的手工裁切，維護成本不可行。→ 因此玻璃質感由「Kit 瀏覽器渲染 + 截圖烘焙」與「原生形狀近似」兩軌提供。
2. **`backdrop-filter` 在 Chromium print-to-PDF 路徑必失效**（Chromium issue 40895818），但 **screenshot 路徑（compositor）完整保留**。→ 烘圖一律用 Playwright `page.screenshot()`，不用 `page.pdf()`。
3. **GIF 幾乎必比 mp4 大且只有 256 色**：深色漸層影片轉 GIF 會有色帶（banding）。`BG_Video/wave.mp4`（1280×720、24fps、10s）本身只有 4.1MB；重壓縮 mp4 可到約 1–2MB。→ 動態背景雙軌都產，mp4 為推薦主用。
4. **投影片母片（slide master / layout）上的影片與動態 GIF 不保證在放映時播放**（PowerPoint 版本行為不一）。→ 動態層放在「範例頁」的最底層物件；版面配置底圖用影片首幀烘焙的靜態圖保底。
5. 深色簡報投影對比感知約掉 30%。→ 內文 ≥ 24pt、字重 ≥ Regular、文字用 off-white、發光僅點綴 KPI。

## 3. 專案結構

```
UI-ToolBox/
  presentation/
    masters/            9 個版型母版 HTML（1920×1080 固定畫布，引用 ../../liquid-glass.css/js + 深色 tokens）
    package.json        僅此子資料夾的 devDependencies（playwright）——Kit 本體維持零依賴，node_modules 不出 presentation/
    bake.mjs            Playwright @2x 截圖腳本
    media.sh            ffmpeg 背景影片處理腳本
    build_pptx.py       python-pptx 組裝 .pptx
    skeleton.pptx       最小空白 master 底檔（build 的起點，見 §4.3）
    assets/             烘圖與媒體產物（backgrounds、chrome、media）
    dist/               最終產物 liquid-glass-dark.pptx
    README.md           使用說明：怎麼改母版、怎麼重烘、怎麼換主題
```

- 母版 HTML 是**視覺單一真相**：版型長相先在瀏覽器裡用真 Kit 調到滿意，再烘進 pptx。
- 遵守 UI-ToolBox 鐵律：不動 `site.src.html` / `SPEC.md` 的既有規格；presentation/ 只**引用** Kit 兩檔，不複製修改。
- 深色 tokens 來源：參照 `docs/case-imarine.md` §5 的深色補充規格（底色、髮絲線、模組色相紀律）。

## 4. 三個腳本的規格

### 4.1 `media.sh`（ffmpeg）

來源：`../iMarine-Carbon-Tokenization-POC/BG_Video/wave.mp4`（1280×720、24fps、10s、4.1MB；上游唯讀，複製一份進 `assets/media/` 後只處理副本）。

| 產物 | 參數 | 目標 |
|---|---|---|
| `wave-loop.mp4` | h264、CRF 28、720p、無音軌，收尾交叉淡接做無縫循環 | 約 1–2MB，推薦主用 |
| `wave-loop.gif` | 12fps、寬 960、`palettegen`（stats_mode=diff）+ `paletteuse` bayer 抖色 | 壓 banding，實測回報大小 |
| `wave-frame.png` | 取影片第 0 秒幀，放大至 1920×1080 | 版面配置的靜態保底底圖原料 |

### 4.2 `bake.mjs`（Playwright，Chromium，deviceScaleFactor=2）

- 逐一載入 `masters/*.html`，viewport 1920×1080，等字型與 Kit init 完成後截圖。
- 三類產物：
  1. **全頁 chrome 底圖**：封面、全幅氛圍頁、Outline 章節卡等主視覺版型——整頁玻璃 chrome（不含可變文字）烘成一張圖。
  2. **乾淨背景圖**：深底 + 光暈 blob +（疊上 `wave-frame.png` 的）靜態波浪——日常版型的版面配置底圖。
  3. **玻璃卡校準參考圖**：單一 `.lg-card` 特寫，供原生形狀配方肉眼比對。

### 4.3 `build_pptx.py`（python-pptx 1.0.2，16:9）

實作途徑（已知的兩個 python-pptx 限制與對策）：
- **公開 API 不支援新建 slide layouts**：以 repo 內附的最小 skeleton .pptx（僅含空白 master）為底，`build_pptx.py` 用 lxml 直接產生/覆寫 9 個 slideLayout XML 部件（placeholder 幾何、底圖填滿）。skeleton 視為建置素材，同樣進版控。
- **`add_movie()` 預設點擊播放**：範例頁的動態背景需在插入後補 timing XML（autoplay + loop + 靜音）；GIF 則以 `add_picture()` 插入即可自動播放。

- **Theme 寫入 tokens**：色票 accent `#35E0A6`、金 `#E9BC63`、資訊藍 `#38BDF8`、警示 `#F0648C`、底 `#070B11`、off-white 文字色；major/minor 字型 Inter + Noto Sans TC（East Asian）。數字/等寬語彙（KPI 大數字、代碼）theme 槽位放不下，由元件庫頁與範例頁的文字框直接指定 Geist Mono。
- **原生玻璃卡配方**（統一由程式寫入，數值經校準頁比對定案）：圓角矩形、深色半透明填色、1px 白 ~10% 髮絲線（上緣稍亮）、柔和外陰影。
- **9 個 slide layouts**（含 placeholder 文字框，底圖依版型用 chrome 圖或乾淨背景圖）：
  1. 封面（大標 + 副標 + 作者列；全頁烘圖）
  2. Outline 章節卡 grid（編號 + eyebrow + 色條；全頁烘圖 + 文字框對位）
  3. 流程 Pipeline（步驟卡 + 箭頭 + 底部 note bar）
  4. 標準內容頁（eyebrow 標頭 + 左列表/文字 + 右主視覺）
  5. 統計卡陣列 + 主視覺（KPI 列語彙同 `.lg-stat`）
  6. 表格頁（styled 表格 + highlight 列）
  7. 多圖比較（2–4 圖並排 + 說明面板）
  8. 全幅氛圍頁（滿版視覺 + 玻璃標題條；全頁烘圖）
  9. 結語 / Thank You（編號結論卡 grid）
- **元件庫頁**（簡報尾端 2–3 頁，全原生形狀供複製）：KPI 卡、note/結論 bar、chip 徽章、styled 表格、編號卡、章節 nav 膠囊、頁腳。
- **範例頁**：每版型一頁填好假內容（通用假資料，非 iMarine 專屬），**最底層埋動態背景（預設 mp4，自動播放 + 循環 + 靜音）**——使用者做新頁的標準動線是「複製範例頁」；「從版面配置新增」則得到靜態底圖版。
- **校準頁**：烘圖卡 vs 原生卡並排一頁，僅開發期產出（`build_pptx.py --calibration` 旗標）；正式 dist 產物不含此頁。

## 5. 使用者動線（模板約定）

- 要動態背景 → 複製範例頁改內容。
- 快速新頁可接受靜態背景 → 從版面配置新增。
- 新元件 → 從元件庫頁複製貼上。
- 字型：需本機安裝 Inter / Noto Sans TC；對外交付時用 PowerPoint「內嵌字型」另存。

## 6. 驗收清單

Owner 在 PowerPoint 實測：
1. 開檔無修復警告；放映時範例頁動態背景會動、會循環。
2. 改字、搬卡、縮放卡片後玻璃觀感不破。
3. 從每個版面配置新增頁面，placeholder 與底圖正確。
4. 元件庫頁元件複製到新頁樣式不跑。
5. GIF 版與 mp4 版並排比較檔案大小與畫質，擇一定為範例頁預設。

開發端基本檢查：LibreOffice / macOS 預覽開檔不炸、python-pptx 重新讀回無 schema 錯誤。

## 7. 風險與對策

| 風險 | 對策 |
|---|---|
| GIF 色帶明顯 | bayer 抖色 + 實測比對；已備 mp4 主路線 |
| 觀看者機器沒裝字型 | 交付檔用內嵌字型另存；README 註明 |
| master 上媒體不播放（版本差異） | 設計上已不依賴：動態層只在範例頁 |
| 原生卡與烘圖卡質感落差 | 校準頁肉眼比對；落差過大的版型改用全頁烘圖 |
| 換主題重烘成本 | 三腳本全參數化，tokens 單點替換 |
| slideLayout XML 手作出錯（開檔修復警告） | 每次 build 後自動用 python-pptx 讀回 + LibreOffice headless 開檔煙霧測試；XML 以最小 skeleton 為底逐步疊加 |
| mp4 autoplay timing XML 在舊版 PowerPoint 行為不同 | 驗收以 owner 實機 PowerPoint 為準；GIF 版天然自動播放可作備援 |

## 8. 未來擴充（本期不做）

- 淡色 Monet 主題第二套。
- 一鍵「HTML 簡報 → 截圖 → 滿版嵌入 .pptx」的靜態匯出工具（若日後要交像素級同款的唯讀版）。
- 收進 UI-ToolBox 展示站與 README 的產品線介紹。
