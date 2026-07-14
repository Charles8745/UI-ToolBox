"""開檔煙霧測試：python-pptx 讀回 + （有裝時）LibreOffice headless 轉檔不炸。"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def dist(tmp_path_factory):
    import build_pptx

    out = tmp_path_factory.mktemp("smoke") / "t.pptx"
    build_pptx.build(out)
    return out


def test_pptx_reads_back(dist):
    prs = Presentation(dist)
    assert len(list(prs.slides)) >= 11  # 9 範例 + 2 元件庫


SOFFICE = shutil.which("soffice") or (
    "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if Path("/Applications/LibreOffice.app").exists() else None)


@pytest.mark.skipif(SOFFICE is None, reason="LibreOffice 未安裝")
def test_libreoffice_converts(dist, tmp_path):
    r = subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(tmp_path), str(dist)],
        capture_output=True, timeout=180)
    assert r.returncode == 0, r.stderr.decode()[:500]
    assert list(tmp_path.glob("*.pdf")), "LibreOffice 未產出 PDF"
