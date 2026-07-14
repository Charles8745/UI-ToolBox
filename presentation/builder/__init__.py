"""presentation builder：從 skeleton.pptx 組裝 Liquid Glass 深色模板。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PX = 6350  # 1 母版 px = 6350 EMU（12192000 / 1920）


def load_tokens() -> dict:
    return json.loads((ROOT / "tokens.json").read_text())
