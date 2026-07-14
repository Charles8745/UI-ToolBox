#!/usr/bin/env bash
# 背景影片處理：來源唯讀，複製副本後產出 mp4 loop / gif loop / 靜態首幀
set -euo pipefail
cd "$(dirname "$0")"
# 來源影片（唯讀）在競賽工作區，非 UI-ToolBox 兄弟目錄；可用 WAVE_SRC 覆寫絕對路徑
SRC="${WAVE_SRC:-../../2026航港大數據創意應用競賽/iMarine-Carbon-Tokenization-POC/BG_Video/wave.mp4}"
OUT="assets/media"
mkdir -p "$OUT"
[ -f "$OUT/wave.mp4" ] || cp "$SRC" "$OUT/wave.mp4"

# 1) 無縫循環 mp4：前 9 秒為主體，最後 1 秒與開頭交叉淡接
ffmpeg -y -i "$OUT/wave.mp4" -filter_complex \
  "[0:v]split[a][b];[a]trim=0:9,setpts=PTS-STARTPTS[a1];[b]trim=9:10,setpts=PTS-STARTPTS[b1];[b1][a1]xfade=transition=fade:duration=1:offset=0[v]" \
  -map "[v]" -an -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p "$OUT/wave-loop.mp4"

# 2) GIF：8fps、寬 640、diff palette + bayer 抖色壓 banding（備援用，主用為 mp4）
ffmpeg -y -i "$OUT/wave-loop.mp4" -vf \
  "fps=8,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  -loop 0 "$OUT/wave-loop.gif"

# 3) 靜態首幀：第 0 秒幀放大至 1920x1080
ffmpeg -y -i "$OUT/wave.mp4" -vf "select=eq(n\,0),scale=1920:1080" -frames:v 1 "$OUT/wave-frame.png"

ls -lh "$OUT"
