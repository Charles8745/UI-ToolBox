# Liquid Glass Kit — 開發指南(給 Claude Code)

零依賴的「液態玻璃」UI 工具包,加上一個用它本身做出來的展示網站(莫內線上展廳 + 元件展示 + AI 整合指南,三分頁、單一 HTML)。

折射原理:以 Snell 定律對凸超橢圓斷面做光線追蹤,產生 SVG 位移貼圖,再用 `backdrop-filter: url(#svg)` 即時折射元件背後的內容。**此效果僅 Chromium 引擎(Chrome / Edge / Arc 等)支援,其他瀏覽器自動降級為磨砂玻璃**。

---

## 建置流程(最重要)

開發只改三個原始檔,改完跑一次建置就會重生單檔 `index.html`:

```bash
python3 build_site.py
```

- 需要 Python 3,無第三方套件。
- `build_site.py` 會把 `liquid-glass.css`、`liquid-glass.js`、`assets/` 的圖檔與 `assets/icons.json` 的圖示,全部內聯進 `site.src.html` 的 `{{...}}` 佔位符,輸出成自足的 `index.html`。
- 任何對 `site.src.html` / `liquid-glass.css` / `liquid-glass.js` / `assets/` 的修改,都要重跑這行才會反映到 `index.html`。

---

## 鐵律(務必遵守)

1. **`site.src.html` 是網站的唯一真實來源**。所有版面與內容改動都直接編輯它。
2. **絕對不要去找或執行 `assemble_*.py`,也不要引入 `partials/`**。那是更早期的片段拼裝流程,且片段已過時;跑它會用舊內容覆蓋掉現有成果。本資料夾已刻意不含這些檔。
3. `site.src.html` 裡的 `{{CSS}}`、`{{JS}}`、`{{ICON_SPRITE}}`、`{{IMG_*}}` 由 `build_site.py` 自動填入,**不要手動展開**。
4. 要用新圖示前,先把該 Phosphor 圖示的 SVG path 加進 `assets/icons.json`(鍵為圖示名,例如 `"trend-up"`)。`site.src.html` 任何 `#ph-xxx` 引用若在 icons.json 找不到,**build 會直接失敗並列出缺少的圖示**。引用時請用完整字面量(例如 JS 裡寫 `'#ph-trend-up'`,不要寫 `'#ph-trend-' + dir`,否則 build 的圖示掃描會抓到斷片而誤判缺圖)。
5. 玻璃只做容器:儀表板的數字、sparkline、圖表是「實心內容層」,內容本身不上玻璃(上了會看不見)。

---

## 檔案結構

```
.
├── CLAUDE.md          ← 本檔
├── site.src.html      ← 網站唯一真實來源(編輯這個)
├── liquid-glass.js    ← 工具包引擎 v1.2.0(編輯這個)
├── liquid-glass.css   ← 工具包樣式(編輯這個)
├── build_site.py      ← 建置腳本:三者 + assets → index.html
├── index.html         ← build 產物(可隨時重生;直接用瀏覽器開即為展示站)
├── README.md          ← 工具包對外使用說明
└── assets/
    ├── icons.json     ← Phosphor 圖示 path(build 必用)
    └── *.jpg          ← 展示站用的莫內畫作與地球貼圖
```

---

## 已知狀態與待人工確認

- 工具包為 **v1.2.0**,含 18 件元件:按鈕、圖示按鈕、卡片、開關、滑桿、分頁、搜尋框、標籤與徽章、工具提示、對話框、導航列、Dock、拖曳,以及儀表板五件(統計卡 `.lg-stat`、進度條 `.lg-meter`、環形儀表 `.lg-gauge`、圖表 `.lg-chart`、通知 `LiquidGlass.toast`)。
- 儀表板的「即時數據」開關以屬性驅動模擬資料跳動;`prefers-reduced-motion` 時亮燈但不自動跳動。
- 折射 / 動畫 / 顯影只能在 Chromium 系瀏覽器實看,程式環境無法渲染驗證。改動視覺後請在瀏覽器確認。

---

## AI 規格書(元件結構與 API 速查)

下面這份規格也呈現在展示站「AI 整合」分頁,是照工具包開發的核心參考:

```text
# Liquid Glass Kit — AI 使用規格
零依賴液態玻璃 UI 工具包(透明玻璃、即時折射、發光背景、拖曳)。
專案內已有兩個檔案:liquid-glass.css、liquid-glass.js。

## 初始化(每頁一次)
<link rel="stylesheet" href="liquid-glass.css">
<script src="liquid-glass.js"></script>
<script>LiquidGlass.init();</script>

## 鐵則
1. 玻璃只用於浮在內容之上的控制層(導航、卡片、面板、對話框、dock);文章、圖片等內容本身不上玻璃。
2. 折射玻璃 = class="lg" + data-lg;小型或大量重複的元件(列表項、標籤)改用 class="lg lg-static"(磨砂、無折射、便宜)。
3. 頁面必須有圖像或多彩背景,玻璃效果才看得見。
4. 不要手寫 backdrop-filter 或自製玻璃 CSS,一律使用工具包的 class 與 API。
5. 動態插入的節點呼叫 LiquidGlass.attach(el);非 Chromium 瀏覽器會自動降級為磨砂,無需處理。
6. 儀表元件(統計卡/進度條/環形儀表/圖表)= 玻璃容器 + 實心內容層:數字、走勢圖、圖表本身不透明,只有外框是玻璃——內容上玻璃會看不見,這是技術上必要的邊界。

## 元件結構
按鈕:<button class="lg lg-btn" data-lg>文字</button>(修飾:lg-btn--pill / --accent / --icon / --lg / --sm)
卡片:<div class="lg lg-card" data-lg><h4 class="lg-card__title">…</h4><p class="lg-card__meta">…</p></div>
導航:<nav class="lg lg-navbar" data-lg><span class="lg-navbar__brand">…</span><span class="lg-navbar__spacer"></span><button class="lg-navbar__link is-active">…</button></nav>
搜尋:<div class="lg lg-search" data-lg><svg>…</svg><input type="search"><kbd>⌘K</kbd></div>
開關:<label class="lg-switch"><input type="checkbox"><span class="lg-switch__track"><span class="lg-switch__thumb"></span></span>標籤</label>
滑桿:<div class="lg lg-slider" data-lg><input class="lg-slider__input" type="range"></div>
分頁:<div class="lg lg-tabs" data-lg role="tablist"><span class="lg-tabs__pill"></span><button class="lg-tabs__tab is-active" role="tab">…</button>…</div>
對話框:<div class="lg-modal" id="m1"><div class="lg-modal__overlay" data-lg-close></div><div class="lg-modal__panel lg" data-lg role="dialog">…</div></div>;以 <button data-lg-open="#m1"> 開啟、data-lg-close 關閉。
Dock:<div class="lg lg-dock" data-lg><button class="lg-dock__item">icon</button>…</div>(自帶鄰近放大)
標籤:<span class="lg-chip">…</span>;徽章:<span class="lg-badge">3</span>
工具提示:任何元素加 data-lg-tip="文字"
拖曳:元素加 data-lg-drag="viewport|parent"(可選 data-lg-drag-handle=".selector"),或 LiquidGlass.draggable(el, { bounds, inertia })
統計卡:<div class="lg lg-stat" data-lg><span class="lg-stat__label">標籤</span><div class="lg-stat__row"><span class="lg-stat__value" data-lg-value="48250" data-lg-prefix="$"></span><span class="lg-stat__delta"><svg><use href="#ph-trend-up"/></svg>12.4%</span></div><svg class="lg-stat__spark" data-lg-spark="28,31,30,36,40,44"></svg></div>(漲綠跌紅:徽章加 lg-stat__delta--down)
進度條:<div class="lg-meter" data-lg-value="68"></div>(本身非玻璃:凹槽軌道 + 實心液體填充,前緣有彎月鼓頭)
環形儀表:<div class="lg lg-gauge" data-lg data-lg-press data-lg-profile="circle" data-lg-value="74" data-lg-unit="%" data-lg-label="Goal"></div>
圖表:<div class="lg lg-chart" data-lg><div class="lg-chart__head"><h4 class="lg-chart__title">標題</h4></div><svg class="lg-chart__svg" data-lg-chart="line" data-lg-points="1240,1390,1180,1620" data-lg-labels="Mon,Tue,Wed,Thu"></svg></div>(data-lg-chart 可為 line 或 bar;手刻 SVG、零依賴、hover 顯數值)
通知:LiquidGlass.toast({ title, message, icon, duration })(JS 呼叫;右下堆疊、自動消退、最多 4 則)
發光背景:<div class="lg-glow" style="--lg-glow-base:#7d92ad;"><div class="lg-glow__image" style="--lg-bg-image:url(bg.jpg);"></div></div>

## 屬性(單一元素覆寫)
data-lg-refraction(折射倍率,預設 1.25)、data-lg-chromatic(色散 0–1)、data-lg-blur、data-lg-saturate、data-lg-bezel(斜面 px)、data-lg-thickness(厚度 px)、data-lg-profile(squircle|circle|lip)
儀表資料(屬性驅動):data-lg-value(統計卡/進度條/環形儀表的目標值)、data-lg-spark(統計卡走勢逗號數列)、data-lg-points + data-lg-labels(圖表資料)、data-lg-prefix / -suffix / -decimals(數字格式)。改變 data-lg-value / -spark / -points 即觸發彈簧動畫(單一 MutationObserver 自動接手,無需手動呼叫)。

## JS API
LiquidGlass.init(config?) / attach(el, opts?) / draggable(el, opts?) / refresh() / toast({ title, message, icon, duration }) / config / supported / reducedMotion

## Tokens(:root 覆寫)
--lg-accent(品牌色,預設 #cf6045)、--lg-tint、--lg-text、--lg-radius-s/m/l/pill、--lg-blur-fallback、--lg-font
主題:<html data-lg-theme="dark">,不設則跟隨系統。
```
