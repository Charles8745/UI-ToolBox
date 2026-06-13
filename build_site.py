#!/usr/bin/env python3
# 組裝 standalone index.html(三分頁網站)
import base64, json, re, sys, os

import os as _os
KIT = _os.path.dirname(_os.path.abspath(__file__))
css = open(f'{KIT}/liquid-glass.css', encoding='utf-8').read()
js = open(f'{KIT}/liquid-glass.js', encoding='utf-8').read()
tpl = open(f'{KIT}/site.src.html', encoding='utf-8').read()
icons = json.load(open(f'{KIT}/assets/icons.json', encoding='utf-8'))

def durl(path):
    return 'data:image/jpeg;base64,' + base64.b64encode(open(path, 'rb').read()).decode()

symbols = ''.join(
    f'<symbol id="ph-{n}" viewBox="0 0 256 256"><path d="{d}"/></symbol>'
    for n, d in sorted(icons.items())
)
sprite = f'<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">{symbols}</svg>'

refs = set(re.findall(r'#ph-([a-z0-9-]+)', tpl))
missing = sorted(r for r in refs if r not in icons)
if missing:
    print('缺少圖示:', missing); sys.exit(1)
print(f'圖示引用 {len(refs)} 種,全部存在')

out = (tpl
       .replace('{{CSS}}', css)
       .replace('{{JS}}', js)
       .replace('{{ICON_SPRITE}}', sprite)
       .replace('{{IMG_PARASOL}}', durl(f'{KIT}/assets/monet.jpg'))
       .replace('{{IMG_BRIDGE}}', durl(f'{KIT}/assets/bridge.jpg'))
       .replace('{{IMG_SUNFLOWERS}}', durl(f'{KIT}/assets/sunflowers.jpg'))
       .replace('{{IMG_MADAME}}', durl(f'{KIT}/assets/madame.jpg'))
       .replace('{{IMG_CLIFFS}}', durl(f'{KIT}/assets/cliffs.jpg'))
       .replace('{{IMG_WHEAT}}', durl(f'{KIT}/assets/wheat.jpg'))
       .replace('{{IMG_ROUEN}}', durl(f'{KIT}/assets/rouen.jpg'))
       .replace('{{IMG_POPPYFIELDS}}', durl(f'{KIT}/assets/poppyfields.jpg'))
       .replace('{{IMG_POPPIES}}', durl(f'{KIT}/assets/poppies.jpg'))
       .replace('{{IMG_POPPIES_XL}}', durl(f'{KIT}/assets/poppies_xl.jpg'))
       .replace('{{IMG_GARDENER}}', durl(f'{KIT}/assets/gardener.jpg'))
       .replace('{{IMG_EARTH}}', durl(f'{KIT}/assets/earth.jpg')))

leftover = re.findall(r'\{\{[A-Z_]+\}\}', out)
if leftover:
    print('未替換:', leftover); sys.exit(1)

open(f'{KIT}/index.html', 'w', encoding='utf-8').write(out)
print(f'index.html 完成:{os.path.getsize(f"{KIT}/index.html")/1024:.0f} KB')
