"""把 tokens 寫進佈景主題：accent1..6 色票與 major/minor 字型。"""
from pptx.opc.constants import CONTENT_TYPE as CT
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.package import PartFactory, XmlPart
from pptx.oxml.ns import qn

# python-pptx 1.0.2 未替 theme content-type 註冊專屬 Part 子類，
# part_related_by(RT.THEME) 預設回傳無 ._element 的通用 Part（僅有 .blob 原始 bytes）。
# PartFactory.part_type_for 是官方公開的擴充點（見其 docstring），用來替
# 指定 content-type 註冊 Part 子類；<a:theme> 元素類別本身已由
# pptx.oxml 註冊為 CT_OfficeStyleSheet，故補註冊 XmlPart 即可讓
# part_related_by(RT.THEME) 回傳具備 ._element（已解析 XML）的 part。
# 必須在任何 Presentation(...) 開啟含 theme part 的檔案「之前」註冊生效。
PartFactory.part_type_for.setdefault(CT.OFC_THEME, XmlPart)


def _theme_element(prs):
    master_part = prs.slide_masters[0].part
    theme_part = master_part.part_related_by(RT.THEME)
    return theme_part._element


def write_theme(prs, tokens: dict) -> None:
    theme = _theme_element(prs)
    scheme = theme.find(qn("a:themeElements")).find(qn("a:clrScheme"))
    for i in range(1, 7):
        node = scheme.find(qn(f"a:accent{i}"))
        for child in list(node):
            node.remove(child)
        srgb = node.makeelement(qn("a:srgbClr"), {"val": tokens[f"accent{i}"]})
        node.append(srgb)

    fonts = theme.find(qn("a:themeElements")).find(qn("a:fontScheme"))
    for tag in ("a:majorFont", "a:minorFont"):
        group = fonts.find(qn(tag))
        group.find(qn("a:latin")).set("typeface", tokens["fontLatin"])
        group.find(qn("a:ea")).set("typeface", tokens["fontEastAsian"])
