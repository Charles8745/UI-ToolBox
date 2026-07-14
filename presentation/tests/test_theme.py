from pathlib import Path

import pytest
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def prs():
    import sys
    sys.path.insert(0, str(ROOT))
    from builder import load_tokens
    from builder.theme import write_theme

    p = Presentation(ROOT / "skeleton.pptx")
    write_theme(p, load_tokens())
    return p


def test_skeleton_is_minimal(prs):
    assert prs.slide_width == 12192000 and prs.slide_height == 6858000
    layouts = list(prs.slide_masters[0].slide_layouts)
    assert [l.name for l in layouts] == ["Blank"]


def test_theme_accents_and_fonts(prs):
    theme = prs.slide_masters[0].part.part_related_by(RT.THEME)._element
    scheme = theme.find(qn("a:themeElements")).find(qn("a:clrScheme"))
    assert scheme.find(qn("a:accent1")).find(qn("a:srgbClr")).get("val") == "35E0A6"
    assert scheme.find(qn("a:accent4")).find(qn("a:srgbClr")).get("val") == "F0648C"
    fonts = theme.find(qn("a:themeElements")).find(qn("a:fontScheme"))
    major = fonts.find(qn("a:majorFont"))
    assert major.find(qn("a:latin")).get("typeface") == "Inter"
    assert major.find(qn("a:ea")).get("typeface") == "Noto Sans TC"
