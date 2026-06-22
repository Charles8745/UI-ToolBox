# 表單控制家族 A — File upload 設計 spec

> 對象:Liquid Glass Kit v0.1,家族 A 第八件(#11),A 家族最後一件。
> 家族共同決策見 Checkbox spec。本件用 per-container init(同 `initTabs`)+ **新增一個圖示**。
> 節奏:做完 build + Chromium 自驗 → 交使用者目視 → 核可。分支 `feat/form-family-a2`(承接 OTP)。
> 日期:2026-06-22。

## File upload · `.lg-upload`(拖放上傳)

**定位:** 玻璃拖放區 + 點擊瀏覽 + 檔案清單(可個別移除)。**UI 控制件——收集檔案進 `<input type="file">`,不做實際網路上傳**(由 consumer 處理)。

### 新增圖示(Task 1 先做)

icons.json 加 `cloud-arrow-up`(Phosphor regular,已取得正確 path):

```json
"cloud-arrow-up": "M178.34,165.66,160,147.31V208a8,8,0,0,1-16,0V147.31l-18.34,18.35a8,8,0,0,1-11.32-11.32l32-32a8,8,0,0,1,11.32,0l32,32a8,8,0,0,1-11.32,11.32ZM160,40A88.08,88.08,0,0,0,81.29,88.68,64,64,0,1,0,72,216h40a8,8,0,0,0,0-16H72a48,48,0,0,1,0-96c1.1,0,2.2,0,3.29.12A88,88,0,0,0,72,128a8,8,0,0,0,16,0,72,72,0,1,1,100.8,66,8,8,0,0,0,3.2,15.34,7.9,7.9,0,0,0,3.2-.68A88,88,0,0,0,160,40Z"
```

引用用完整字面量 `#ph-cloud-arrow-up`。檔案列另用既有 `#ph-file-text`、移除鈕用 `#ph-x`。

### 結構

```html
<div class="lg lg-upload" data-lg data-lg-upload>
  <input type="file" class="lg-upload__input" multiple aria-label="選擇檔案">
  <div class="lg-upload__prompt">
    <svg class="lg-upload__icon" viewBox="0 0 256 256"><use href="#ph-cloud-arrow-up"/></svg>
    <p class="lg-upload__title">拖放檔案到這裡,或 <strong>點擊瀏覽</strong></p>
    <p class="lg-upload__hint">支援多檔</p>
  </div>
  <ul class="lg-upload__list"></ul>   <!-- 選檔後 initUpload 渲染 -->
</div>
```

- 面板 = `lg + data-lg`(折射玻璃大面板)+ `data-lg-upload`(JS 標記);玻璃只做面板,檔名/大小/圖示是實心內容層。
- `<input type="file">` **不用 `hidden`**,改 CSS 視覺隱藏但**仍可鍵盤聚焦**(`position:absolute;opacity:0;width:1px;height:1px`);搭配 `.lg-upload:focus-within` ring → 鍵盤可 Tab 到、Space/Enter 開檔案對話框,**無需額外 JS 處理鍵盤**。

### 行為(JS = `initUpload(panel)`,per-container,同 `initTabs` 範式)

以 `DataTransfer` 為**單一真實來源**(`store`),支援拖放與瀏覽**合併** + **個別移除** + 回寫 `input.files`:

- **點擊面板**(非清單區)→ `input.click()` 開對話框。clicking 清單/移除鈕不觸發(`if (e.target.closest('.lg-upload__list')) return`)。
- **dragenter/dragover** → `preventDefault` + `is-dragover`;**dragleave/drop** → 移除 `is-dragover`(drop 另 `preventDefault`)。
- **drop / input change** → 取檔案,**去重**(同 name+size 跳過),`store.items.add(f)`,`input.files = store.files`,渲染。
- **移除鈕** → `store.items.remove(idx)`,`input.files = store.files`,重渲染。
- 渲染:清單每列 = `#ph-file-text` + 檔名 + 格式化大小(B/KB/MB)+ `#ph-x` 移除鈕;有檔時面板加 `has-files`。

`DataTransfer` / `input.files = dt.files` / `items.add` / `items.remove(i)` 皆 Chromium 支援;非 Chromium 仍可點擊瀏覽 + 顯示(drag API 缺則拖放靜默不動,點擊照常)。

### 狀態

| 狀態 | 視覺 |
|---|---|
| default | 折射玻璃面板,置中 icon + 提示 |
| **dragover** | accent ring(**保留 `.lg` 基底陰影**:`box-shadow: var(--lg-shadow), 0 0 0 2px var(--lg-accent)`)+ 可選底色微亮 |
| focus(鍵盤) | `.lg-upload:focus-within` 同款 accent ring |
| has-files | 清單顯示於提示下方 |
| disabled | `.lg-upload--disabled { opacity:.5; pointer-events:none }`(demo 同時對 input 加原生 `disabled`) |

### token / 版面

- 面板:`--lg-radius-l` 圓角、min-height 約 160px、padding、`text-align:center`;icon 約 40px、`color:var(--lg-text-dim)`;`__title` 用 `--lg-text`、`strong` 用 `--lg-accent`;`__hint` 用 `--lg-text-dim`。dragover/focus ring 用 `--lg-accent` + `var(--lg-shadow)`。不硬編色。
- 清單列:小字、`--lg-text`,大小用 `--lg-text-dim`,移除鈕 hover 提亮。

### 範圍邊界(YAGNI,v1 不做)

- 實際網路上傳 / 進度條、檔案類型或大小驗證、圖片預覽縮圖、單檔模式(預設 `multiple`;要單檔由 consumer 拿掉 `multiple`)、清單拖曳排序。

### 整合位置

1. **icons.json 加 `cloud-arrow-up`**(上方 path);CSS 進 `liquid-glass.css`(輸入框家族附近,如 `.lg-otp` 之後);reduced-motion 區補 `.lg-upload`(ring 過渡)。
2. JS:`liquid-glass.js` 加 `initUpload(panel)`(放 `initOtp` 附近),`boot()` 加 `[].forEach.call(document.querySelectorAll('[data-lg-upload]'), initUpload)`。
3. `site.src.html` 元件展示加 Upload tile(一般 + disabled),用較寬 tile(t3)。
4. CLAUDE.md AI 規格書「元件結構」段補 `檔案上傳` 一行 + 「屬性」段提 `data-lg-upload`;AI Guide 程式碼庫補 `<details>`(`data-snippet="upload"`)。
5. `python3 build_site.py` 重生 `index.html`(會檢查 `cloud-arrow-up` 在 icons.json),Chromium 自驗。

### 驗收

- 點面板 → 開檔案對話框、選檔 → 清單顯示檔名+大小;再選/拖放更多 → 合併、去重;點某列 `x` → 移除該檔。
- 拖檔案到面板上方 → 顯 accent ring + 提示(放開後加入);鍵盤 Tab 到面板 → focus ring,Space 開對話框。
- 折射顯影;disabled 面板半透明不可互動;深色對比 OK。
- 非 Chromium:磨砂降級、點擊瀏覽 + 清單正常(拖放可能不作用但不報錯)、無 console 錯誤。
- reduced-motion:ring 無過渡突跳。

### 風險

中(本家族最複雜)。新東西:新圖示(已取得正確 path)、drag 事件 + `DataTransfer` 檔案管理(add/remove/回寫 input.files)、折射面板 ring 保留基底陰影。drag/DataTransfer 是標準 Web API;per-container init、ring 手法皆有既有範式。
