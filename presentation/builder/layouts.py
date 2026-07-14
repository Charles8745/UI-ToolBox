"""slide layout 引擎：clone Blank layout、鋪背景圖、放 placeholder。
python-pptx 公開 API 不支援新建 layout，此處以 part 層 clone + lxml 完成。"""
import copy

from lxml import etree
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.oxml.ns import qn
from pptx.parts.slide import SlideLayoutPart

from . import PX, ROOT

NSMAP = (
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)

ALIGN = {"l": "l", "c": "ctr", "r": "r"}


def _next_layout_partname(package) -> PackURI:
    nums = [
        int(part.partname.filename[len("slideLayout"):-len(".xml")])
        for part in package.iter_parts()
        if str(part.partname).startswith("/ppt/slideLayouts/slideLayout")
    ]
    return PackURI(f"/ppt/slideLayouts/slideLayout{max(nums) + 1}.xml")


def _clone_blank_layout(master, name: str):
    blank = master.slide_layouts[0]
    src_part = blank.part
    package = src_part.package
    el = copy.deepcopy(src_part._element)
    new_part = SlideLayoutPart(_next_layout_partname(package), src_part.content_type, package, el)
    new_part.relate_to(master.part, RT.SLIDE_MASTER)
    r_id = master.part.relate_to(new_part, RT.SLIDE_LAYOUT)

    id_lst = master.element.find(qn("p:sldLayoutIdLst"))
    max_id = max((int(e.get("id")) for e in id_lst), default=2147483648)
    entry = id_lst.makeelement(qn("p:sldLayoutId"), {"id": str(max_id + 1)})
    entry.set(qn("r:id"), r_id)
    id_lst.append(entry)

    el.find(qn("p:cSld")).set("name", name)
    return new_part


def _set_background(layout_part, image_path: str) -> None:
    image_part, r_id = layout_part.get_or_add_image_part(str(ROOT / image_path))
    bg = etree.fromstring(
        f"<p:bg {NSMAP}><p:bgPr><a:blipFill>"
        f'<a:blip r:embed="{r_id}"/><a:stretch><a:fillRect/></a:stretch>'
        "</a:blipFill><a:effectLst/></p:bgPr></p:bg>"
    )
    c_sld = layout_part._element.find(qn("p:cSld"))
    old = c_sld.find(qn("p:bg"))
    if old is not None:
        c_sld.remove(old)
    c_sld.insert(0, bg)


def _add_placeholder(layout_part, spec: dict, sp_id: int, tokens: dict) -> None:
    ph_attr = 'type="title"' if spec["ph_type"] == "title" else f'type="body" idx="{spec["idx"]}"'
    algn = ALIGN[spec.get("align", "l")]
    bold = "1" if spec["b"] else "0"
    sp = etree.fromstring(
        f"<p:sp {NSMAP}>"
        f'<p:nvSpPr><p:cNvPr id="{sp_id}" name="ph{sp_id}"/>'
        '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        f"<p:nvPr><p:ph {ph_attr}/></p:nvPr></p:nvSpPr>"
        "<p:spPr><a:xfrm>"
        f'<a:off x="{spec["x"] * PX}" y="{spec["y"] * PX}"/>'
        f'<a:ext cx="{spec["w"] * PX}" cy="{spec["h"] * PX}"/>'
        '</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        '<p:txBody><a:bodyPr/><a:lstStyle>'
        f'<a:lvl1pPr algn="{algn}"><a:defRPr sz="{spec["sz"] * 100}" b="{bold}">'
        f'<a:solidFill><a:srgbClr val="{spec["color"]}"/></a:solidFill>'
        f'<a:latin typeface="{tokens["fontLatin"]}"/><a:ea typeface="{tokens["fontEastAsian"]}"/>'
        "</a:defRPr></a:lvl1pPr></a:lstStyle>"
        "<a:p><a:r><a:t>佔位文字</a:t></a:r></a:p></p:txBody></p:sp>"
    )
    layout_part._element.find(qn("p:cSld")).find(qn("p:spTree")).append(sp)


def build_layouts(prs, tokens: dict) -> dict:
    from .layouts_spec import LAYOUTS

    master = prs.slide_masters[0]
    for spec in LAYOUTS:
        part = _clone_blank_layout(master, spec["name"])
        _set_background(part, spec["background"])
        for i, ph in enumerate(spec["placeholders"]):
            _add_placeholder(part, ph, sp_id=100 + i, tokens=tokens)
    return {l.name: l for l in master.slide_layouts}
