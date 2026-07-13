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
- `build_site.py` 會把 `liquid-glass.css`、`liquid-glass.js`、`assets/` 的圖檔、`assets/icons.json` 的圖示,以及根目錄 `SPEC.md` 的規格全文,全部內聯進 `site.src.html` 的 `{{...}}` 佔位符,輸出成自足的 `index.html`。
- 任何對 `site.src.html` / `liquid-glass.css` / `liquid-glass.js` / `assets/` / `SPEC.md` 的修改,都要重跑這行才會反映到 `index.html`。

---

## 鐵律(務必遵守)

1. **`site.src.html` 是網站的唯一真實來源**。所有版面與內容改動都直接編輯它。
2. **絕對不要去找或執行 `assemble_*.py`,也不要引入 `partials/`**。那是更早期的片段拼裝流程,且片段已過時;跑它會用舊內容覆蓋掉現有成果。本資料夾已刻意不含這些檔。
3. `site.src.html` 裡的 `{{CSS}}`、`{{JS}}`、`{{ICON_SPRITE}}`、`{{IMG_*}}`、`{{AI_SPEC}}` 由 `build_site.py` 自動填入,**不要手動展開**。
4. 要用新圖示前,先把該 Phosphor 圖示的 SVG path 加進 `assets/icons.json`(鍵為圖示名,例如 `"trend-up"`)。`site.src.html` 任何 `#ph-xxx` 引用若在 icons.json 找不到,**build 會直接失敗並列出缺少的圖示**。引用時請用完整字面量(例如 JS 裡寫 `'#ph-trend-up'`,不要寫 `'#ph-trend-' + dir`,否則 build 的圖示掃描會抓到斷片而誤判缺圖)。
5. 玻璃只做容器:儀表板的數字、sparkline、圖表是「實心內容層」,內容本身不上玻璃(上了會看不見)。
6. **元件規格只改 `SPEC.md` 一處**(單一真相)。新增或修改元件時同步更新 SPEC.md;展示站由 build 注入、README 與 AGENTS.md 只指路,不要在任何檔案再造規格副本。

---

## 檔案結構

```
.
├── CLAUDE.md          ← 本檔
├── SPEC.md            ← 元件規格單一真相(build 注入展示站,新元件先改這裡)
├── site.src.html      ← 網站唯一真實來源(編輯這個)
├── liquid-glass.js    ← 工具包引擎 v0.1(編輯這個)
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

- 工具包為 **v0.1**,含 26 件元件:按鈕、圖示按鈕、卡片、開關、滑桿、分頁、搜尋框、標籤與徽章、工具提示、對話框、導航列、Dock、拖曳,表單家族八件(文字輸入 `.lg-field`、多行輸入 `.lg-field--area`、核取方塊 `.lg-check`、單選 `.lg-radio`、步進器 `.lg-stepper`、星等評分 `.lg-rating`、驗證碼 `.lg-otp`、檔案上傳 `.lg-upload`),以及儀表板五件(統計卡 `.lg-stat`、進度條 `.lg-meter`、環形儀表 `.lg-gauge`、圖表 `.lg-chart`、通知 `LiquidGlass.toast`)。
- 儀表板的「即時數據」開關以屬性驅動模擬資料跳動;`prefers-reduced-motion` 時亮燈但不自動跳動。
- 折射 / 動畫 / 顯影只能在 Chromium 系瀏覽器實看,程式環境無法渲染驗證。改動視覺後請在瀏覽器確認。

---

## 已知陷阱:動態建立的玻璃在「整頁重載 / SPA」可能不顯影折射(Chromium)

**症狀**:用 JS 動態建立 `.lg [data-lg]` 面板(SPA、框架渲染、或 dev server 存檔觸發的整頁重載)後,面板只剩平面磨砂底色、**沒有折射**;但只要存一次 CSS 檔(dev server 的 CSS 熱抽換)折射就「突然出現」。純靜態 HTML(`file://`,濾鏡在首次繪製前就存在)通常正常,所以這個 bug 看起來時有時無。`attach()` 有呼叫、`el._lgGlass` 也在、`backdrop-filter: url(#lg-f-N)` 也掛上了 —— 但就是沒合成。

**根因**:折射用 SVG `<filter>` 的 `<feImage>`,位移貼圖是 canvas `toDataURL()` 的 PNG **data-URI,Chromium 非同步解碼**。面板的 `backdrop-filter` 合成節點在「首次繪製」就被光柵化(那時 PNG 還沒解碼完),而 Chromium **不會在貼圖解碼完成後重建這個合成節點** → 面板停在「只有底色、無折射」,直到一次**文件層級的樣式重算**強迫重建。

**為什麼存 CSS 檔會修好**:dev server 換掉 `<link>` / 注入 `<style>`,改變「有效樣式表集合」→ 觸發 Blink 全文件 style 重算 → 重新解析 `url(#filter)` 並用**已解碼**的 `feImage` 重建合成節點。
**為什麼改 inline 樣式沒用**:`el.style.*` 或 `documentElement.style.setProperty('--var',…)` 只是單一元素的快速重算,不會重新解析 SVG 資源、也不會重建合成節點。切 `opacity`、改 CSS 變數都救不回來。

**可靠解法(實測有效)**:面板建立並 `attach()` 後,**等位移貼圖解碼穩定**,再對每個面板做「拆掉 backdrop-filter → 還原 → 換一個同源 `<link rel=stylesheet>`(clone + cache-bust)」。**兩半缺一不可**(單獨換樣式表、或單獨拆 inline 都不穩)。解碼時間因機器而異,實務上**在載入後頭幾秒多打幾次**最穩:

```js
function reviveGlass(root = document) {
  const panels = [...root.querySelectorAll('[data-lg]')];
  const saved = panels.map(el => [el, el.style.backdropFilter, el.style.getPropertyValue('-webkit-backdrop-filter')]);
  saved.forEach(([el,a,b]) => { if (a||b) { el.style.backdropFilter='none'; el.style.setProperty('-webkit-backdrop-filter','none'); } });
  requestAnimationFrame(() => {
    saved.forEach(([el,a,b]) => { if (a) el.style.backdropFilter=a; if (b) el.style.setProperty('-webkit-backdrop-filter',b); });
    const link = [...document.querySelectorAll('link[rel="stylesheet"]')].reverse()
      .find(e => { try { return new URL(e.href).origin === location.origin; } catch { return false; } });
    if (!link) return;
    const base = link.href.split('?')[0];
    const clone = link.cloneNode();
    clone.href = base + (base.includes('?') ? '&' : '?') + 'lgrc=' + Date.now();
    clone.addEventListener('load', () => link.remove(), { once: true });
    link.after(clone);
  });
}
// 動態建立面板後:
[400, 900, 1800, 3500].forEach(ms => setTimeout(reviveGlass, ms));
```

**注意**:`lg-fallback`(非 Chromium / 不支援折射)走純 CSS `backdrop-filter: blur()`,**不受此問題影響**;`LiquidGlass.supported === false` 時直接略過。每次 revive 會有約一影格的拆除閃爍,折射已顯影後再打會閃一下,可在確定的延遲點只打一次以消除。
**待辦(工具包可內建)**:把上述 revive 收進 `LiquidGlass`(`attach()` 後自動排程,或提供 `LiquidGlass.recomposite()`),讓使用者不必自己處理。發現於一個把本工具包當動態 HUD 的 SPA 專案。

---

## 實戰案例(patterns 層)

深色主題、儀表板、多模組介面的需求,先讀 `docs/case-imarine.md`(iMarine 案例:深色 tokens、頁面節奏、模組色相紀律、背景層與 scrim),再動手拼版面。其 §5 是可接在 SPEC.md 之後使用的補充規格。

---

## 元件規格(單一真相:SPEC.md)

元件結構、屬性、JS API、材質與 tokens 的完整規格在根目錄 **`SPEC.md`** —— 它是唯一真相:`build_site.py` 會把它注入展示站「AI 整合」分頁,README 與 AGENTS.md 只指路。新增或修改元件時,規格只改 SPEC.md 一處。
