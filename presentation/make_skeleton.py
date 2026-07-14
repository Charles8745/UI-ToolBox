"""產生最小 skeleton.pptx：16:9、單 master、僅留 Blank layout、master 背景 #070B11。
執行一次，產物進版控；build_pptx.py 以它為起點。"""
from pptx import Presentation
from pptx.util import Emu
from pptx.oxml.ns import qn
from lxml import etree

NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'


def main():
    prs = Presentation()
    prs.slide_width = Emu(12192000)
    prs.slide_height = Emu(6858000)
    master = prs.slide_masters[0]

    # 只留名為 Blank 的 layout，其餘從 sldLayoutIdLst 與 rels 移除
    id_lst = master.element.find(qn("p:sldLayoutIdLst"))
    for layout in list(master.slide_layouts):
        if layout.name == "Blank":
            continue
        for sld_id in list(id_lst):
            r_id = sld_id.get(qn("r:id"))
            if master.part.related_part(r_id) is layout.part:
                master.part.drop_rel(r_id)
                id_lst.remove(sld_id)
                break

    # master 背景設實心 #070B11（任何縫隙都保持深色）
    bg = etree.fromstring(
        f'<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" {NS}>'
        '<p:bgPr><a:solidFill><a:srgbClr val="070B11"/></a:solidFill>'
        "<a:effectLst/></p:bgPr></p:bg>"
    )
    c_sld = master.element.find(qn("p:cSld"))
    c_sld.insert(0, bg)

    prs.save("skeleton.pptx")
    print("skeleton.pptx 已產生；layouts =", [l.name for l in prs.slide_masters[0].slide_layouts])


if __name__ == "__main__":
    main()
