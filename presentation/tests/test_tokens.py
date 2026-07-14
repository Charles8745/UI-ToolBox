import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_css_tokens_match_json():
    tokens = json.loads((ROOT / "tokens.json").read_text())
    css = (ROOT / "masters" / "theme-dark.css").read_text()
    for key in ["bg", "surface", "text", "textDim"] + [f"accent{i}" for i in range(1, 7)]:
        css_var = {"textDim": "text-dim"}.get(key, key)
        m = re.search(rf"--{css_var}:\s*#([0-9A-Fa-f]{{6}})", css)
        assert m, f"theme-dark.css 缺 --{css_var}"
        assert m.group(1).upper() == tokens[key].upper(), f"--{css_var} 與 tokens.json 不一致"
    assert f'--hairline: rgba(255, 255, 255, .{tokens["hairlineAlpha"]:02d})' in css
