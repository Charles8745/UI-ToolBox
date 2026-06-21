# iOS 26 行為升級 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 iOS 26 招牌「行為」(同心圓角、兩材質、捲動縮小、捲動邊緣淡出、按鈕 morph)加進 Liquid Glass Kit 既有元件,不新增元件。

**Architecture:** 全部沿用既有引擎結構 —— 行為進 `liquid-glass.js`、樣式進 `liquid-glass.css`。同心圓角掛 `Glass.update()`;材質讀 classList 套 preset;捲動類用一支共用 scroll util;morph 用 Web Animations API(FLIP)接管 modal 開關。每項一個 Task = 一個檢查點。

**Tech Stack:** 零依賴 vanilla JS(ES5 風格,與現有碼一致)、CSS、`python3 build_site.py` 建置、chrome-devtools 在 Chromium 實機驗證。

## Global Constraints

- **零依賴**:不得引入任何第三方套件;JS 維持現有 ES5 風格(`var`、`function`,不用 ES6+ 語法糖以免與既有碼不一致)。
- **折射僅 Chromium**:非 Chromium(`LiquidGlass.supported === false` / `.lg-fallback`)走磨砂降級,每個行為都要確保 fallback 不報錯。
- **唯一真實來源**:網站改 `site.src.html`,**絕不手改 `index.html`**;改完一律 `python3 build_site.py` 重生(圖示完整性需通過)。
- **圖示用完整字面量**;新圖示先進 `assets/icons.json`(本計畫不需新圖示)。
- **玻璃只做容器**:內容層不上玻璃。
- **版號維持 `0.1.0`**,不動 `version`。
- **無自動化測試**:本專案無 test runner。每個 Task 的「驗證」= `python3 build_site.py` 通過 + chrome-devtools 開 `index.html` 在 Chromium 實看(折射 + `.lg-fallback` 磨砂兩條都顧)+ 交使用者檢查。
- **reduced-motion**:沿用既有 `REDUCED_MOTION`(`liquid-glass.js:27`)慣例 —— 定態/即時顯示,不自動動。

---

## File Structure

- `liquid-glass.js` — 所有行為邏輯(applyConcentric、材質 preset、scroll util、shrink、scroll-edge、morph)。
- `liquid-glass.css` — 所有樣式(token 化硬編圓角、`lg--regular`、`is-condensed`、scroll-edge 不需 CSS、morph 的 keyframe 閘門)。
- `site.src.html` — 各行為的實機展示(元件展示分頁)。
- `CLAUDE.md` — AI 規格書補對應屬性說明。
- `index.html` — build 產物,每 Task 重生,不手改。

執行順序即檢查點順序:**Task 1 (B4) → 2 (B6) → 3 (B1) → 4 (B5) → 5 (B3)**。

---

## Task 1: B4 同心圓角(JS 自動推算)

**Files:**
- Modify: `liquid-glass.js`(新增 `applyConcentric()`;`Glass` 建構子讀旗標;`Glass.update()` 末尾呼叫)
- Modify: `liquid-glass.css`(`.lg-dock__item` 14px、`.lg-tooltip` 13px → token)
- Modify: `site.src.html`(元件展示分頁加一個巢狀同心圓角 demo)
- Modify: `CLAUDE.md`(AI 規格書「屬性」段補 `data-lg-concentric`)

**Interfaces:**
- Produces: `applyConcentric(el)` — 對帶 `data-lg-concentric` 的元素寫入四角 `borderRadius`;由 `boot()` 對所有 `[data-lg-concentric]` 統一呼叫並掛 ResizeObserver(不依賴 Glass,fallback 亦生效)。

- [ ] **Step 1: 在 `liquid-glass.js` 的 `readRadius`(約 line 294)後新增 `applyConcentric`**

```js
function applyConcentric(el) {
  var parent = el.parentElement;
  while (parent && !parent.classList.contains('lg')) parent = parent.parentElement;
  if (!parent) return;                       // 找不到 lg 父層 → no-op
  function r(v) { return parseFloat(v) || 0; }
  var pcs = getComputedStyle(parent);
  var ptl = r(pcs.borderTopLeftRadius), ptr = r(pcs.borderTopRightRadius),
      pbr = r(pcs.borderBottomRightRadius), pbl = r(pcs.borderBottomLeftRadius);
  if (!(ptl || ptr || pbr || pbl)) return;   // 父無圓角 → no-op
  var prc = parent.getBoundingClientRect(), crc = el.getBoundingClientRect();
  var gapL = crc.left - prc.left - r(pcs.borderLeftWidth);
  var gapT = crc.top - prc.top - r(pcs.borderTopWidth);
  var gapR = prc.right - crc.right - r(pcs.borderRightWidth);
  var gapB = prc.bottom - crc.bottom - r(pcs.borderBottomWidth);
  var MIN = 4;
  function corner(prad, ga, gb) { return Math.max(prad - Math.max(ga, gb), MIN); } // 角由相鄰兩邊定義,取大者
  el.style.borderTopLeftRadius     = corner(ptl, gapL, gapT) + 'px';
  el.style.borderTopRightRadius    = corner(ptr, gapR, gapT) + 'px';
  el.style.borderBottomRightRadius = corner(pbr, gapR, gapB) + 'px';
  el.style.borderBottomLeftRadius  = corner(pbl, gapL, gapB) + 'px';
}
```

- [ ] **Step 2: 在 `boot()`(line 1237 起)對所有 `[data-lg-concentric]` 跑一輪(不掛 Glass,fallback 也生效)**

concentric **不要**掛在 `Glass.update()`——非 Chromium 時 `attach()` 回傳 no-op stub(`liquid-glass.js:404`)、`Glass` 根本不建立,掛 update 會讓 fallback 下的 concentric 完全失效。改在 boot() 統一處理,並**同時觀察元素自身與其 lg 父層**(父 padding 改變、或固定尺寸子被平移時都能重算;只觀察子自身時固定尺寸子的 content-box 不變→不觸發):

於 `init()` 的 `boot()` 內、`[].forEach.call(document.querySelectorAll('[data-lg]'), ...)` 之後加入:

```js
      [].forEach.call(document.querySelectorAll('[data-lg-concentric]'), function (n) {
        applyConcentric(n);
        if (typeof ResizeObserver === 'undefined') return;
        var ro = new ResizeObserver(function () { applyConcentric(n); });
        ro.observe(n);
        var p = n.parentElement;
        while (p && !p.classList.contains('lg')) p = p.parentElement;
        if (p) ro.observe(p);   // 父層尺寸/內距變動也重算
      });
```

(applyConcentric 對折射面板與 fallback 面板一視同仁;Glass 的折射照舊由它自己的 RO 維護,互不干涉。)

- [ ] **Step 3: `liquid-glass.css` — 硬編圓角收進 token(不位移外觀)**

`--lg-radius-s` 實為 12px(`liquid-glass.css:52`),直接套會把 dock 角 14→12、tooltip 13→12,外觀會走樣。故先在 token 區(line 51-55 附近)新增貼近原值的一級:

```css
  --lg-radius-xs: 14px;
```

再把硬編圓角改用它:
- `.lg-dock__item`(約 line 578)`border-radius: 14px;` → `border-radius: var(--lg-radius-xs);`(同值,純收進 token)
- `.lg-tooltip`(約 line 547)`border-radius: 13px;` → `border-radius: var(--lg-radius-xs);`(13→14,1px 內肉眼難辨)

- [ ] **Step 4: `site.src.html` 元件展示分頁加 demo**

在元件展示分頁(卡片/容器區附近)插入一個外層大圓角玻璃、內層帶 `data-lg-concentric` 的巢狀示例:

```html
<div class="lg lg-card" data-lg style="border-radius:28px;padding:14px;">
  <div class="lg lg-static" data-lg-concentric style="padding:14px;">同心圓角:內層自動 = 28 − 14(外層內距)</div>
</div>
```

(角 inset = 外層 padding(14)= 子相對父的 gap;內層自己的 padding 不參與半徑計算。外層 padding 設 14 才讓「28 − 14」成立。)

- [ ] **Step 5: `CLAUDE.md` AI 規格書「## 屬性」段補一行**

```text
data-lg-concentric(同心圓角:子半徑自動 = 最近 lg 父層半徑 − 內距,四角各算)
```

- [ ] **Step 6: 建置**

Run: `python3 build_site.py`
Expected: 無錯誤、列出圖示完整性通過、`index.html` 重生。

- [ ] **Step 7: Chromium 實機自驗(chrome-devtools 開 `index.html`)**

確認:巢狀玻璃內外圓角同心;改父 `padding`(demo 內層為流式寬,父層也被觀察)內層半徑跟著變;未帶 `data-lg-concentric` 的元件不受影響;dock item 圓角不變(14px)、tooltip 13→14px 肉眼無感;**`.lg-fallback`(非 Chromium)下 concentric 仍生效**(已改由 boot 處理、不依賴 Glass)且不報 console 錯。截圖。

- [ ] **Step 8: 交使用者檢查 [CHECKPOINT]** — 核可後才往下。

- [ ] **Step 9: 核可後 Commit**

```bash
git add liquid-glass.js liquid-glass.css site.src.html CLAUDE.md index.html
git commit -m "B4 同心圓角:data-lg-concentric 自動推算 + 硬編圓角收進 token"
```

---

## Task 2: B6 Regular / Clear 兩材質(modifier class)

**Files:**
- Modify: `liquid-glass.js`(新增 `MATERIALS` preset;`Glass.update()` 的 refraction/blur/saturate 改為「data-attr > 材質 > config」)
- Modify: `liquid-glass.css`(`.lg-fallback .lg--regular` 加重磨砂)
- Modify: `site.src.html`(展示 clear vs regular 對比)
- Modify: `CLAUDE.md`(AI 規格書補材質 class)

**Interfaces:**
- Consumes: `Glass.update()` 既有 `o`(opts)、`config`。
- Produces: `MATERIALS`(`{ clear, regular }`,各含 `blur`/`saturate`/`refraction`);`lg--clear`/`lg--regular` modifier 語意。

- [ ] **Step 1: `liquid-glass.js` — `config` 物件(line 85 `};` 後)新增材質 preset**

```js
  // 材質變體(B6):現狀 = Clear;Regular 較霧較不透,內容上可讀(數值可實機微調)
  var MATERIALS = {
    clear:   { blur: 1.6, saturate: 1.55, refraction: 1.25 },
    regular: { blur: 7.0, saturate: 1.20, refraction: 0.90 }
  };
```

> 註:spec line 67 寫「覆寫 `--lg-blur` / `--lg-saturate` token」,但這兩個 token **不存在**(CSS 只有 `--lg-blur-fallback` / `--lg-saturate-fallback`,且只走 fallback 路徑)。折射模式的 blur/saturate 由 JS 的 `feGaussianBlur` / `feColorMatrix` 控,故改以此 JS preset 覆寫(spec line 68 的 JS 路徑),才是唯一可行解;fallback 端另由 Step 4 的 CSS 補。

- [ ] **Step 2: `Glass.update()` 改 refraction/blur/saturate 取值(line 354、361-362)**

把原本三行:

```js
    var refraction = isNaN(o.refraction) ? config.refraction : o.refraction;
```
…(及 line 361-362 的 blur / sat)替換為:先解析材質,再以「data-attr > 材質 > config」取值。於 `var o = this.opts;`(line 342)後就近加入材質解析,並改寫三個取值點:

```js
    var mat = elm.classList.contains('lg--regular') ? MATERIALS.regular
            : elm.classList.contains('lg--clear')   ? MATERIALS.clear : null;
```

refraction(line 354)改為:
```js
    var refraction = !isNaN(o.refraction) ? o.refraction : (mat ? mat.refraction : config.refraction);
```
blur(line 361)改為:
```js
    var blur = !isNaN(o.blur) ? o.blur : (mat ? mat.blur : config.blur);
```
sat(line 362)改為:
```js
    var sat = !isNaN(o.saturate) ? o.saturate : (mat ? mat.saturate : config.saturate);
```

(注意:`elm` 在 update 內為 `this.el`,line 338 已有 `var elm = this.el;`。)

- [ ] **Step 3: classList 變更要能即時重繪 → 確認 `setOptions`/`update` 可由外部呼叫**

無需新 API;切 class 後呼叫 `el._lgGlass.update()` 即生效。展示站若有切換鈕,綁定時呼叫它。

- [ ] **Step 4: `liquid-glass.css` — fallback 下的 regular 加重磨砂(特異度要壓過既有降級規則)**

既有降級規則 `html.lg-fallback .lg`(line 119-122,特異度 0,2,1)也命中 regular 面板(它同時帶 `.lg`)。若只寫 `.lg-fallback .lg--regular`(0,2,0)會**輸給**既有規則、完全不生效(Step 8 的「regular 更糊」會無聲失敗)。要用 `html.lg-fallback .lg.lg--regular`(0,3,0)穩勝,且 blur/saturate 都覆寫:

於 line 119-123 的降級規則**之後**新增:

```css
html.lg-fallback .lg--regular,
html.lg-fallback .lg.lg--regular {
  -webkit-backdrop-filter: blur(calc(var(--lg-blur-fallback) * 1.7)) saturate(1.2);
  backdrop-filter: blur(calc(var(--lg-blur-fallback) * 1.7)) saturate(1.2);
}
```

- [ ] **Step 5: `site.src.html` — clear vs regular 對比 demo**

元件展示分頁加兩塊同內容、分別掛 `lg--clear` / `lg--regular` 的面板並列:

```html
<div class="lg lg-card lg--clear" data-lg><h4 class="lg-card__title">Clear(預設)</h4><p class="lg-card__meta">媒體上更通透</p></div>
<div class="lg lg-card lg--regular" data-lg><h4 class="lg-card__title">Regular</h4><p class="lg-card__meta">內容上更可讀</p></div>
```

- [ ] **Step 6: `CLAUDE.md` AI 規格書補材質 class**

「## 元件結構」或 token 段補:
```text
材質變體:class 加 lg--clear(預設,較透)或 lg--regular(較霧,內容上用)。優先序:單元素 data-lg-* > 材質 class > 全域 config。
```

- [ ] **Step 7: 建置** — Run: `python3 build_site.py` / Expected: 通過、重生。

- [ ] **Step 8: Chromium 實機自驗** — clear vs regular 觀感明顯不同;`lg--regular` 在內容上可讀、`lg--clear` 在圖上通透;對同一面板額外加 `data-lg-refraction="2"` 確認仍能覆寫材質;`.lg-fallback` 下 regular 確實更糊(驗特異度修正生效)、`lg--clear` 在 fallback 即等於 `.lg` 預設磨砂(無專屬規則,屬預期)、皆不報錯。截圖。

- [ ] **Step 9: 交使用者檢查 [CHECKPOINT]**

- [ ] **Step 10: 核可後 Commit**

```bash
git add liquid-glass.js liquid-glass.css site.src.html CLAUDE.md index.html
git commit -m "B6 兩材質:lg--clear / lg--regular modifier(data-attr > 材質 > config)"
```

---

## Task 3: B1 捲動縮小 + 共用 scroll util(navbar + tabs)

**Files:**
- Modify: `liquid-glass.js`(新增 `makeScrollWatcher` / `getWindowScroll` / `initScrollShrink`;`initTabs` 暴露 `_lgRepositionPill`;`boot()` 接線)
- Modify: `liquid-glass.css`(`is-condensed` 樣式 + transition)
- Modify: `site.src.html`(navbar/tabs 加 `data-lg-shrink`,並確保該分頁可捲動以觸發)
- Modify: `CLAUDE.md`(AI 規格書補 `data-lg-shrink`)

**Interfaces:**
- Produces:
  - `makeScrollWatcher(target)` → `{ subscribe(cb) }`,cb 收 `{ y, dy, atTop, atBottom }`(rAF 合批)。
  - `getWindowScroll()` → 單例 window watcher。
  - `initScrollShrink()` — 對 `[data-lg-shrink]` 接 window watcher 切 `is-condensed`。
  - `root._lgRepositionPill()`(掛在每個 `.lg-tabs`)— 無動畫重定位藥丸。
- Consumes(Task 4 用):`makeScrollWatcher` / `getWindowScroll`。

- [ ] **Step 1: `liquid-glass.js` — 新增共用 scroll util(放在 `initTabs` 前,約 line 545)**

```js
  /* 共用 scroll util(B1 建立,B5 沿用):單一 listener + rAF 合批 */
  function makeScrollWatcher(target) {
    var t = target || window, subs = [], raf = 0;
    function getY() { return t === window ? (window.scrollY || window.pageYOffset || 0) : t.scrollTop; }
    function maxY() {
      return t === window
        ? (document.documentElement.scrollHeight - window.innerHeight)
        : (t.scrollHeight - t.clientHeight);
    }
    var lastY = getY();
    function tick() {
      raf = 0;
      var y = getY(), m = maxY();
      var s = { y: y, dy: y - lastY, atTop: y <= 1, atBottom: y >= m - 1 };
      lastY = y;
      subs.forEach(function (cb) { cb(s); });
    }
    t.addEventListener('scroll', function () { if (!raf) raf = requestAnimationFrame(tick); }, { passive: true });
    return {
      subscribe: function (cb) { subs.push(cb); var y0 = getY(); cb({ y: y0, dy: 0, atTop: y0 <= 1, atBottom: y0 >= maxY() - 1 }); }   // 初次 atBottom 實算:不可捲動容器才不會被誤淡底緣
    };
  }
  var _winScroll = null;
  function getWindowScroll() { return _winScroll || (_winScroll = makeScrollWatcher(window)); }
```

- [ ] **Step 2: `initTabs` 暴露無動畫重定位(在 line 581-582 的 active 區塊前)**

於 `initTabs` 內、`tabs.forEach(...)` 之後加入:

```js
    root._lgRepositionPill = function () {
      var act = root.querySelector('.lg-tabs__tab.is-active') || tabs[0];
      if (act && pill) { pill.style.width = act.offsetWidth + 'px'; pill.style.left = act.offsetLeft + 'px'; }
    };
```

- [ ] **Step 3: `liquid-glass.js` — 新增 `initScrollShrink`(放在 scroll util 後)**

```js
  function initScrollShrink() {
    var bars = [].slice.call(document.querySelectorAll('[data-lg-shrink]'));
    if (!bars.length || REDUCED_MOTION) return;   // reduced-motion:定在展開態
    var THRESH = 6;
    getWindowScroll().subscribe(function (s) {
      bars.forEach(function (bar) {
        var want = s.y < 24 ? false : s.dy > THRESH ? true : s.dy < -THRESH ? false : bar.classList.contains('is-condensed');
        if (bar.classList.contains('is-condensed') === want) return;
        bar.classList.toggle('is-condensed', want);
        if (bar.classList.contains('lg-tabs') && bar._lgRepositionPill && !bar._lgPillPending) {
          bar._lgPillPending = true;   // 防快速連切堆疊多個 listener
          bar.addEventListener('transitionend', function te(e) {
            if (e.target !== bar || e.propertyName.indexOf('padding') !== 0) return; // 只認 bar 自身的 padding 過渡,忽略子 tab 冒泡(否則量到半途 rect)
            bar._lgPillPending = false;
            bar.removeEventListener('transitionend', te);
            bar._lgRepositionPill();
          });
        }
      });
    });
  }
```

- [ ] **Step 4: `boot()` 接線(line 1250 `initPress();` 後)**

```js
      initScrollShrink();
```

- [ ] **Step 5: `liquid-glass.css` — is-condensed 樣式 + transition**

```css
.lg-navbar[data-lg-shrink],
.lg-tabs[data-lg-shrink] { transition: padding var(--lg-speed) var(--lg-ease); }

.lg-navbar.is-condensed { padding-top: 4px; padding-bottom: 4px; }
.lg-navbar.is-condensed .lg-navbar__brand,
.lg-navbar.is-condensed .lg-navbar__link {
  padding-top: 5px; padding-bottom: 5px; font-size: 0.88em;
  transition: padding var(--lg-speed) var(--lg-ease), font-size var(--lg-speed) var(--lg-ease);
}
.lg-tabs.is-condensed { padding: 3px; }
.lg-tabs.is-condensed .lg-tabs__pill { top: 3px; bottom: 3px; }   /* pill 垂直硬編 5px;隨容器 padding 收成 3px 才貼合 condensed tab */
.lg-tabs.is-condensed .lg-tabs__tab {
  padding-top: 6px; padding-bottom: 6px; font-size: 0.9em;
  transition: padding var(--lg-speed) var(--lg-ease), font-size var(--lg-speed) var(--lg-ease);
}
```

(數值可實機微調。)

- [ ] **Step 6: `site.src.html` — 標記 navbar 與 tabs**

給展示用的 navbar 與一組 tabs 加 `data-lg-shrink`;確認該分頁內容夠長能捲動(必要時在 demo 區下方補佔位內容以觸發 window 捲動)。

- [ ] **Step 7: `CLAUDE.md` AI 規格書補一行**

```text
data-lg-shrink(navbar / tabs:下捲縮小、上捲展開;監聽 window 捲動,reduced-motion 定展開態)
```

- [ ] **Step 8: 建置** — Run: `python3 build_site.py` / Expected: 通過、重生。

- [ ] **Step 9: Chromium 實機自驗** — 下捲 navbar/tabs 縮小、上捲展開;捲動微抖不亂跳;**tabs 縮小後藥丸水平對準 active tab 且垂直貼合**(驗 transitionend 重定位 + condensed pill top/bottom);`prefers-reduced-motion` 模擬下定在展開態;`.lg-fallback` 不報錯。截圖。

- [ ] **Step 10: 交使用者檢查 [CHECKPOINT]**

- [ ] **Step 11: 核可後 Commit**

```bash
git add liquid-glass.js liquid-glass.css site.src.html CLAUDE.md index.html
git commit -m "B1 捲動縮小:navbar/tabs data-lg-shrink + 共用 scroll util(tabs 藥丸 transitionend 重定位)"
```

---

## Task 4: B5 Scroll edge effect(漸層遮罩 mask)

**Files:**
- Modify: `liquid-glass.js`(新增 `initScrollEdge`,沿用 Task 3 的 `makeScrollWatcher`;`boot()` 接線)
- Modify: `site.src.html`(一個可捲動容器加 `data-lg-scroll-edge`)
- Modify: `CLAUDE.md`(AI 規格書補 `data-lg-scroll-edge`)

**Interfaces:**
- Consumes: `makeScrollWatcher(target)`(Task 3 提供)。
- Produces: `initScrollEdge()` — 對 `[data-lg-scroll-edge]` 容器**直接套動態 `mask-image`**。

- [ ] **Step 1: `liquid-glass.js` — 新增 `initScrollEdge`(放在 `initScrollShrink` 後)**

```js
  function initScrollEdge() {
    [].slice.call(document.querySelectorAll('[data-lg-scroll-edge]')).forEach(function (el) {
      var mode = el.getAttribute('data-lg-scroll-edge') || 'both';
      var useTop = mode === 'top' || mode === 'both';
      var useBot = mode === 'bottom' || mode === 'both';
      var FADE = 28; // 漸隱帶 px(可實機微調)
      makeScrollWatcher(el).subscribe(function (s) {
        var t = useTop && !s.atTop ? FADE : 0;
        var b = useBot && !s.atBottom ? FADE : 0;
        var m = 'linear-gradient(to bottom, transparent 0, #000 ' + t + 'px, #000 calc(100% - ' + b + 'px), transparent 100%)';
        el.style.webkitMaskImage = m;
        el.style.maskImage = m;
      });
    });
  }
```

(mask 直接掛容器,相對 box 定位、不隨內容捲動 —— 標準作法,無需 sticky 覆蓋層。)

- [ ] **Step 2: `boot()` 接線(line 1250,`initScrollShrink();` 後)**

```js
      initScrollEdge();
```

- [ ] **Step 3: `site.src.html` — 可捲動容器 demo**

**scroll-edge 不要套在 `data-lg` 折射面板本身** —— `mask-image` 會連同該元素的 `backdrop-filter` 折射層與 `.lg::before`/`::after` 的邊緣高光/描邊一起裁切,玻璃邊緣會出現半透明「破口」(fallback 下也會吃掉 rim/描邊)。改成:外層玻璃面板不捲動、不上 mask;內層放一個**非玻璃**的捲動 div 帶屬性:

```html
<div class="lg lg-card" data-lg style="padding:8px;">
  <div data-lg-scroll-edge="both" style="height:200px;overflow:auto;">
    <!-- 一段夠長的內容,捲動時上下緣淡出;mask 只裁內容、不碰折射與 rim -->
  </div>
</div>
```

- [ ] **Step 4: `CLAUDE.md` AI 規格書補一行**

```text
data-lg-scroll-edge="top|bottom|both"(捲動容器:內容捲到上/下緣自動漸隱;mask 直接掛容器,到頂/到底對應緣不淡)
```

- [ ] **Step 5: 建置** — Run: `python3 build_site.py` / Expected: 通過、重生。

- [ ] **Step 6: Chromium 實機自驗** — 容器內容捲動時上/下緣漸隱無硬邊;到頂時頂緣不淡、到底時底緣不淡;**內容不足以捲動的容器上下都不淡**(驗 subscribe 初次 atBottom 實算);改 `data-lg-scroll-edge="top"` 只上緣生效;漸隱帶**不隨內容捲動**;**外層玻璃面板的折射層與邊緣高光/描邊未被 mask 淡掉**(驗 mask 套在內層非玻璃 div);`.lg-fallback` 下 mask 仍生效。截圖。

- [ ] **Step 7: 交使用者檢查 [CHECKPOINT]**

- [ ] **Step 8: 核可後 Commit**

```bash
git add liquid-glass.js site.src.html CLAUDE.md index.html
git commit -m "B5 scroll edge:data-lg-scroll-edge 容器動態 mask 漸隱"
```

---

## Task 5: B3 按鈕 morph(modal + 通用 helper)

**Files:**
- Modify: `liquid-glass.js`(新增 `morphFrom`;`initModals` 的 `open`/`close` 接 origin + WAAPI;click handler 傳觸發按鈕)
- Modify: `liquid-glass.css`(新增 `.lg-modal__panel.is-morphing { animation:none }` 抑制 keyframe;既有預設入場與 reduced-motion 覆寫不動)
- Modify: `site.src.html`(modal 展示維持原狀即可;morph 由觸發按鈕自動帶 origin)
- Modify: `CLAUDE.md`(AI 規格書補 morph 說明)

**Interfaces:**
- Consumes: `initModals` 既有 `open`/`close`/`lastFocus`、`.lg-modal__panel`。
- Produces: `morphFrom(originEl, panel)` — FLIP 從按鈕補間到面板;`panel._lgOrigin` 存觸發來源供關閉反向。

- [ ] **Step 1: `liquid-glass.css` — 用 `.is-morphing` 抑制 keyframe(不動既有預設入場)**

⚠️ **不要**把既有液滴入場改成 opt-in(`.is-droplet`)。原方案有三個連鎖回歸:
1. 站台 paintingModal 等 lightbox 是繞過 `initModals.open()`、直接 `classList.add('is-open')` 開的(`site.src.html:2152`),拿不到 opt-in class → **失去入場動畫**。
2. 既有 reduced-motion 覆寫 `.lg-modal.is-open .lg-modal__panel { animation:none }`(`liquid-glass.css:535-537`,特異度 0,3,0)會被新的 `.is-droplet`(0,4,0)蓋過 → reduced-motion 下反而播動畫。
3. open() 在 reduced-motion 時 `morphed=false` 一定加 `is-droplet`,踩穿 reduced-motion 鐵則。

**正確做法(反向):保留** `.lg-modal.is-open .lg-modal__panel`(`liquid-glass.css:524-528`,含 `opacity:1; transform:none; animation: lg-droplet …`)**原樣不動**;只新增一條 morph 時抑制 keyframe 的規則,讓 WAAPI 獨佔:

```css
.lg-modal__panel.is-morphing { animation: none !important; }
```

`@keyframes lg-droplet`(529-534)與 reduced-motion 覆寫(535-537)**都不動** —— 預設入場、bypass 開啟、reduced-motion 三者行為皆與現況一致;只有 morph 路徑多掛 `is-morphing` 關掉 keyframe(且 morph 只在 `!REDUCED_MOTION` 時發生)。

- [ ] **Step 2: `liquid-glass.js` — 新增 `morphFrom`(放在 `initModals` 前)**

```js
  function morphFrom(origin, panel) {
    // 量測前先中性化 transform:is-open 的 transition 在 t=0 尚未推進,面板仍是 base 的
    // scale(0.86) translateY(18px),直接量會量到縮放盒 → FLIP 的 sx/sy/dx/dy 全偏(實測差約 14%/33px)。
    var savedTrans = panel.style.transition;
    panel.style.transition = 'none';
    panel.style.transform = 'none';
    var o = origin.getBoundingClientRect(), p = panel.getBoundingClientRect(); // 強制 reflow → 真正靜止盒
    panel.style.transform = '';            // 交回 CSS(is-open = transform:none)
    panel.style.transition = savedTrans;
    if (!p.width || !p.height) return false;
    var dx = (o.left + o.width / 2) - (p.left + p.width / 2);
    var dy = (o.top + o.height / 2) - (p.top + p.height / 2);
    var sx = Math.max(o.width / p.width, 0.05), sy = Math.max(o.height / p.height, 0.05);
    panel.animate([
      { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(' + sx.toFixed(3) + ',' + sy.toFixed(3) + ')', opacity: 0.4 },
      { transform: 'none', opacity: 1 }
    ], { duration: 420, easing: 'cubic-bezier(.2,.8,.2,1)' });
    return true;  // 全程保留折射(不關 backdrop-filter)
  }
```

- [ ] **Step 3: `initModals` — `open` 接受 origin(改 line 597-604)**

```js
    function open(modal, origin) {
      lastFocus = document.activeElement;
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden', 'false');
      var panel = modal.querySelector('.lg-modal__panel');
      if (FULL) instances.forEach(function (g) { if (modal.contains(g.el)) g.update(); });
      var morphed = false;
      if (panel && origin && !REDUCED_MOTION && panel.animate) {
        panel.classList.add('is-morphing');                   // 抑制 keyframe,WAAPI 獨佔
        morphed = morphFrom(origin, panel);
        if (!morphed) panel.classList.remove('is-morphing');  // 量不到盒 → 回退既有預設 keyframe
      }
      if (panel) panel._lgOrigin = morphed ? origin : null;
      var f = modal.querySelector('button, [href], input, [tabindex]');
      if (f) f.focus();
    }
```

- [ ] **Step 4: `initModals` — `close` 反向 morph(改 line 605-609)**

```js
    function finishClose(modal) {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      var panel = modal.querySelector('.lg-modal__panel');
      if (panel) panel.classList.remove('is-morphing');   // 清乾淨,下次開啟才正常
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    function close(modal) {
      var panel = modal.querySelector('.lg-modal__panel');
      if (panel && panel._lgOrigin && !REDUCED_MOTION && panel.animate) {
        var o = panel._lgOrigin.getBoundingClientRect(), p = panel.getBoundingClientRect();
        var dx = (o.left + o.width / 2) - (p.left + p.width / 2);
        var dy = (o.top + o.height / 2) - (p.top + p.height / 2);
        var sx = Math.max(o.width / p.width, 0.05), sy = Math.max(o.height / p.height, 0.05);
        var anim = panel.animate([
          { transform: 'none', opacity: 1 },
          { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(' + sx.toFixed(3) + ',' + sy.toFixed(3) + ')', opacity: 0.3 }
        ], { duration: 300, easing: 'cubic-bezier(.4,0,.7,.2)' });
        anim.onfinish = function () { finishClose(modal); };
      } else {
        finishClose(modal);
      }
    }
```

- [ ] **Step 5: `initModals` — click handler 傳觸發按鈕(改 line 611-616,含 `return;` 與閉合括號)**

```js
      var t = e.target.closest ? e.target.closest('[data-lg-open]') : null;
      if (t) {
        var m = document.querySelector(t.getAttribute('data-lg-open'));
        if (m) open(m, t);     // t = 觸發按鈕,作為 morph origin
        return;
      }
```

- [ ] **Step 6: `CLAUDE.md` AI 規格書補 morph 說明**

「對話框」段補:
```text
morph:由 <button data-lg-open> 開啟時,對話框會從該按鈕變形長出(FLIP);ESC / data-lg-close 收回按鈕。reduced-motion 或無觸發按鈕時降級為液滴動畫。
```

- [ ] **Step 7: 建置** — Run: `python3 build_site.py` / Expected: 通過、重生。

- [ ] **Step 8: Chromium 實機自驗** — 點 `data-lg-open` 按鈕→面板**從按鈕位置精準變形長出**(驗 morphFrom 量測中性化:起點對齊按鈕、無偏移錯位);ESC / 關閉鈕→收回按鈕;**全程保留折射**,觀察 morph 過程折射是否穩定;**站台 paintingModal 等 bypass 開啟的 lightbox 入場液滴動畫未退化**(它們不走 open()、無 origin,保留既有 keyframe);`prefers-reduced-motion` 下 modal 開啟**仍是定態/即時**(既有 `animation:none` 覆寫照常生效,未被 is-morphing 影響);`.lg-fallback` 不報錯。截圖。
  - ⚠️ **若 morph 過程折射抽圓角/變形不穩**:回報使用者,啟用 contingency —— `morphFrom` 補間期間 `panel.style.backdropFilter='none'`、`anim.onfinish` 依 reviveGlass 思路**還原原值**(非清空;若面板上有 `-webkit-` 前綴一併還原)並 nudge。此為**contingency,非預設**。

- [ ] **Step 9: 交使用者檢查 [CHECKPOINT]**

- [ ] **Step 10: 核可後 Commit**

```bash
git add liquid-glass.js liquid-glass.css site.src.html CLAUDE.md index.html
git commit -m "B3 按鈕 morph:modal 開關 FLIP(全程保留折射,無 origin 降級液滴)"
```

---

## 完成後

五項全做完後,更新 `HANDOFF.md`:把「iOS 26 招牌行為」表 B1/B3/B4/B5 標記完成、B2 註記待 #14、新增的屬性(`data-lg-concentric` / `lg--regular` / `data-lg-shrink` / `data-lg-scroll-edge`)併入元件清單。

---

## Self-Review(對照 spec)

**Spec coverage:**
- 共用 scroll util → Task 3 Step 1(B1 建立)、Task 4 Step 1 沿用 ✅
- B4 同心圓角 + 硬編圓角收 token → Task 1 ✅
- B6 兩材質 + 優先序(data-attr > 材質 > config)→ Task 2 Step 2 ✅
- B1 navbar+tabs + tabs 藥丸 transitionend 重定位 → Task 3 Step 2-3、Step 9 ✅
- B5 直接 mask 容器 + 動態 stops + 上下緣可分別開關 → Task 4 ✅
- B3 modal+通用 morphFrom + `is-morphing` 抑制 keyframe(保留既有預設入場)+ 全程保留折射 + 無 origin 降級 → Task 5 ✅
- reduced-motion / fallback 每 Task 驗證步驟都列 ✅
- 能力邊界(只能 Chromium 實看)→ Global Constraints + 各 Step 9 ✅

**Placeholder scan:** 無 TBD/TODO;數值微調點均已給可運作初值(非佔位)。

**Type consistency:** `makeScrollWatcher`/`getWindowScroll`/`_lgRepositionPill`/`morphFrom`/`_lgOrigin`/`is-condensed`/`is-morphing` 跨 Task 命名一致;cb payload `{ y, dy, atTop, atBottom }` Task 3 定義、Task 4 消費一致。

---

## Round 2 修正(多代理對抗 review,2026-06-21)

對著真實原始碼跑 6 維度 × 對抗驗證,確認 20 項、修進計畫(駁回 1 項:morph 折射 contingency 旁註無效):

**Major(5)**
- **B5 mask 裁掉折射層**:scroll-edge 從 `data-lg` 玻璃面板移到**內層非玻璃捲動 div**(Task 4 Step 3),避免 mask 連 backdrop-filter 折射與 `.lg::before` rim/描邊一起淡掉造成邊緣破口。
- **B3 paintingModal 入場退化**:站台 lightbox 繞過 `open()` 直接切 `is-open`;改用 **`.is-morphing` 抑制 keyframe**(非把入場改 opt-in),保留既有預設入場(Task 5 Step 1/3)。
- **B3 reduced-motion 回歸 ×2**(兩發現同源):`.is-droplet`(0,4,0)會蓋過 reduced-motion 的 `animation:none`(0,3,0);改 `is-morphing` 後 reduced-motion 區塊完全不動、行為一致。
- **B3 FLIP 量測偏掉**:morphFrom 在 is-open transition t=0 量到 `scale(0.86)` 縮放盒(實測偏 ~14%/33px);量測前先中性化 transform(Task 5 Step 2)。
- **B6 fallback 特異度**:`.lg-fallback .lg--regular`(0,2,0)輸給既有 `html.lg-fallback .lg`(0,2,1),regular 加重磨砂無聲失效;改 `html.lg-fallback .lg.lg--regular`(0,3,0)+ 補 saturate(Task 2 Step 4)。

**Minor / Nit(15)**
- B4 concentric 改由 boot 統一處理(修 fallback 失效)、觀察父層(修固定尺寸子不重算)、新增 `--lg-radius-xs:14px`(dock/tooltip 不位移)、demo 數學改 28−14(外層內距)。
- B6 註記 spec 點名的 `--lg-blur`/`--lg-saturate` token 不存在、改走 JS preset;Step 8 澄清 fallback clear=預設。
- B1 scroll watcher 初次 `atBottom` 實算、transitionend 加 `e.target===bar` 守衛 + 防堆疊、condensed 藥丸 top/bottom 垂直貼合。
- B3 CSS/click handler 行號錨點校正(524-528 / 611-616)。
