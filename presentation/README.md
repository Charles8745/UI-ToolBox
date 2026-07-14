# Liquid Glass Presentation Template

用 Liquid Glass Kit 產出的深色 PowerPoint 模板（16:9）。產物：`dist/liquid-glass-dark.pptx`。

## 管線

    ./media.sh            # 背景影片 -> loop mp4 / gif / 靜態首幀（需 ffmpeg）
    node bake.mjs         # 母版 HTML -> @2x 底圖（需 npm install 過）
    python3 build_pptx.py # 組裝 .pptx（--calibration 附校準頁）
    python3 -m pytest tests -v

## 使用約定

- 要動態波浪背景：**複製範例頁**改內容（動態層是頁上最底層的影片物件）。
- 快速新頁（靜態背景）：從版面配置新增，九個 LG 版型任選。
- 新元件：從簡報尾端的元件庫頁複製 KPI 卡、note bar、chip、編號卡、表格。
- 字型：需安裝 Inter、Noto Sans TC、Geist Mono；對外交付前用 PowerPoint「內嵌字型」另存。
- 投影可讀性：內文不小於 24pt，發光僅限 KPI 數字。

## 換主題

改 `tokens.json` + `masters/theme-dark.css`（測試把關同步）→ 依序重跑三段管線。

## 已知限制

- 影片 autoplay/loop 由 timing XML 寫入，舊版 PowerPoint 行為可能不同；GIF 版（assets/media/wave-loop.gif）為備援。
- 母版 HTML 的玻璃是真 backdrop-filter；PPT 原生卡為近似配方，以 `--calibration` 頁比對。
