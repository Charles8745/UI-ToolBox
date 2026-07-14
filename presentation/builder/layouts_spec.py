"""9 個 slide layout 的幾何規格。座標 px（1920x1080 畫布），build 時乘 PX 轉 EMU。
ph_type: 'title' 或 'body'；body 必帶 idx >= 1。color 為 hex 字串。"""

TEXT = "F5F7FA"
DIM = "9FB0C0"

LAYOUTS = [
    {
        "name": "LG 封面",
        "background": "assets/chrome/cover.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 180, "y": 360, "w": 1040, "h": 220, "sz": 54, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 180, "y": 600, "w": 1000, "h": 60, "sz": 22, "b": False, "color": DIM, "align": "l"},
            {"ph_type": "body", "idx": 2, "x": 180, "y": 706, "w": 1000, "h": 50, "sz": 16, "b": False, "color": DIM, "align": "l"},
        ],
    },
    {
        "name": "LG Outline",
        "background": "assets/chrome/outline.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 460, "y": 56, "w": 1000, "h": 90, "sz": 38, "b": True, "color": TEXT, "align": "c"},
        ],
    },
    {
        "name": "LG 流程",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
        ],
    },
    {
        "name": "LG 內容",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
            {"ph_type": "body", "idx": 2, "x": 96, "y": 300, "w": 980, "h": 588, "sz": 18, "b": False, "color": TEXT, "align": "l"},
        ],
    },
    {
        "name": "LG 統計",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
            {"ph_type": "body", "idx": 2, "x": 1104, "y": 884, "w": 720, "h": 50, "sz": 16, "b": False, "color": DIM, "align": "c"},
        ],
    },
    {
        "name": "LG 表格",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
        ],
    },
    {
        "name": "LG 比較",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 96, "y": 100, "w": 1400, "h": 90, "sz": 40, "b": True, "color": TEXT, "align": "l"},
            {"ph_type": "body", "idx": 1, "x": 96, "y": 56, "w": 900, "h": 40, "sz": 15, "b": True, "color": "35E0A6", "align": "l"},
        ],
    },
    {
        "name": "LG 氛圍",
        "background": "assets/chrome/atmosphere.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 140, "y": 830, "w": 1100, "h": 120, "sz": 44, "b": True, "color": TEXT, "align": "l"},
        ],
    },
    {
        "name": "LG 結語",
        "background": "assets/backgrounds/bg-dark.png",
        "placeholders": [
            {"ph_type": "title", "idx": None, "x": 260, "y": 60, "w": 1400, "h": 100, "sz": 44, "b": True, "color": TEXT, "align": "c"},
            {"ph_type": "body", "idx": 1, "x": 260, "y": 750, "w": 1400, "h": 100, "sz": 44, "b": True, "color": "35E0A6", "align": "c"},
            {"ph_type": "body", "idx": 2, "x": 260, "y": 870, "w": 1400, "h": 50, "sz": 16, "b": False, "color": DIM, "align": "c"},
        ],
    },
]
