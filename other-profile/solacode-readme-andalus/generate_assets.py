#!/usr/bin/env python3
"""
Profile README generator: "Andalus" — Alhambra Illuminated Edition
Authentic Cordoban/Alhambra architecture (alfiz frames, radiating polychrome
voussoirs, polylobed horseshoe arches, stepped Almohad merlons, shaded muqarnas
vaulting, swaying brass lanterns, 8-fold zellige starwork), HarfBuzz/PangoCairo
vectorized Arabic calligraphy (Aref Ruqaa Bold & Amiri Bold), and layered
GitHub-safe CSS/SVG animations. Reads central data from ../../profile-data.json.
"""
import base64
import ctypes
import html
import io
import json
import math
import re
import textwrap
from ctypes import POINTER, Structure, byref, c_char_p, c_double, c_int, c_void_p
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
ASSETS = ROOT / "assets"
FONTS_DIR = ROOT / "fonts"
ASSETS.mkdir(parents=True, exist_ok=True)
DATA = json.loads((REPO_ROOT / "profile-data.json").read_text(encoding="utf-8"))

NAME_1, NAME_2 = DATA["profile"]["first_name"], DATA["profile"]["last_name"]
FULL_NAME = DATA["profile"]["name"]
HANDLE = DATA["profile"]["handle"]
GITHUB = DATA["links"]["github"]
PORTFOLIO = DATA["links"]["portfolio"]
PORTFOLIO_DISPLAY = DATA["links"]["portfolio_display"]
LINKEDIN = DATA["links"]["linkedin"]
ROLE = "SOFTWARE ENGINEER"
PILLARS = DATA["pillars"]
TAGLINE = DATA["profile"]["tagline_lines"]
ABOUT = " ".join(DATA["profile"]["about"])
FACTS = DATA["profile"]["facts"]
FOCUS = "Focus: " + DATA["profile"]["focus"]
STATUS = DATA["profile"].get("status", "Open to opportunities")
LOCATION = DATA["profile"].get("location", "Morocco")

JOURNEY = [
    ("C / C++", "Systems"),
    ("Python", "Backend & AI"),
    ("TypeScript", "Web & Tools"),
    ("Docker", "Infrastructure"),
    ("Linux", "DevOps"),
]
SKILLS = [(s["name"], s["short"]) for s in DATA["skills"]]
PROJECTS = DATA["projects"]

# 6 square crop boxes in art/source.jpg (736x1097)
PROJECT_CROPS = [
    (130, 410, 310, 590),
    (170, 140, 370, 340),
    (400, 380, 640, 620),
    (20, 770, 260, 1010),
    (440, 810, 660, 1030),
    (480, 120, 720, 360),
]

FOOTER_1 = "Build  ·  Explore  ·  Understand"
FOOTER_2 = "Software Engineering  ·  Systems  ·  AI  ·  Mathematics"

AR = dict(
    name="سُلَيْمَان ",
    role="مهندس برمجيات",
    about="نبذة عني",
    journey="رحلتي",
    skills="التقنيات والمهارات",
    projects="مشاريع حية",
    footer_words=("ابنِ", "اكتشف", "افهم"),
    brand="ناشر تك",
)
AR_NUMS = "\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668"
ART_CREDIT = "Artwork: Teal Newcomb (Metal Kirin)"
ART_CAPTION = "Artwork: Teal Newcomb"
SOURCE = ROOT / "art" / "source.jpg"
HERO_CROP = (0, 115, 736, 1097)

SERIF = "Georgia,'Iowan Old Style','Palatino Linotype','DejaVu Serif',serif"
SANS = "'Trebuchet MS','Segoe UI',Verdana,'DejaVu Sans',sans-serif"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Consolas,Menlo,monospace"
ARAB_FALLBACK = "'Aref Ruqaa','Amiri','Scheherazade New','Noto Naskh Arabic',serif"

# Jewel-toned Andalusian zellige glaze palette
TILES_DARK = ["#1F8B7E", "#C85339", "#6EA68A", "#8677C2"]
TILES_LIGHT = ["#1B7A6E", "#B6472E", "#5A8E74", "#6E5FA8"]

THEMES = {
    "dark": dict(
        mode="dark",
        bg="#071211",
        bg_mid="#0E221F",
        bg2="#15312C",
        panel="#0E221F",
        panel2="#173530",
        panel_deep="#091614",
        ink="#F6EDD8",
        soft="#BBD0C4",
        muted="#83A094",
        accent="#E8AE72",
        accent2="#D6684B",
        gold="#D8AE52",
        gold_hi="#FAF0C4",
        gold_lo="#8F671F",
        live="#4EE89E",
        line="#D8AE52",
        band="#050D0C",
        btn="#A8422B",
        btn2="#7E2B19",
        btntxt="#FFF7E3",
        seal="#B8472F",
        seal2="#7D2918",
        glow="#9E8DD4",
        warm="#F7C96B",
        star="#FBE9B2",
        tiles=TILES_DARK,
        tile_op="0.14",
        shadow_op="0.45",
        muq_shade="#071311",
    ),
    "light": dict(
        mode="light",
        bg="#F8F1E1",
        bg_mid="#F1E6CE",
        bg2="#E5D7B9",
        panel="#FDF9EE",
        panel2="#F1E7D1",
        panel_deep="#E7DAC0",
        ink="#132D29",
        soft="#425F58",
        muted="#6A8079",
        accent="#A43D26",
        accent2="#1D756A",
        gold="#B5892D",
        gold_hi="#E6C672",
        gold_lo="#7C5815",
        live="#128252",
        line="#B5892D",
        band="#132D29",
        btn="#A8422B",
        btn2="#7D2A18",
        btntxt="#FFF8E8",
        seal="#A83F28",
        seal2="#752616",
        glow="#8A7BC2",
        warm="#E5A93D",
        star="#B5892D",
        tiles=TILES_LIGHT,
        tile_op="0.16",
        shadow_op="0.14",
        muq_shade="#24423C",
    ),
}


# ---------------------------------------------------------------------------
# HarfBuzz / PangoCairo Arabic Calligraphy Vectorizer (100% GitHub-safe SVG)
# ---------------------------------------------------------------------------
class _PangoRectangle(Structure):
    _fields_ = [("x", c_int), ("y", c_int), ("width", c_int), ("height", c_int)]


class _CairoPathDataHeader(Structure):
    _fields_ = [("type", c_int), ("length", c_int)]


class _CairoPathDataPoint(Structure):
    _fields_ = [("x", c_double), ("y", c_double)]


class _CairoPathData(ctypes.Union):
    _fields_ = [("header", _CairoPathDataHeader), ("point", _CairoPathDataPoint)]


class _CairoPath(Structure):
    _fields_ = [("status", c_int), ("data", POINTER(_CairoPathData)), ("num_data", c_int)]


class _ArabicShaper:
    def __init__(self, fonts_dir: Path):
        self.available = False
        self._cache = {}
        try:
            self.libfc = ctypes.CDLL("libfontconfig.so.1")
            self.libcairo = ctypes.CDLL("libcairo.so.2")
            self.libpango = ctypes.CDLL("libpango-1.0.so.0")
            self.libpc = ctypes.CDLL("libpangocairo-1.0.so.0")
            self.libgobj = ctypes.CDLL("libgobject-2.0.so.0")

            self.libfc.FcConfigAppFontAddDir.argtypes = [c_void_p, c_char_p]
            self.libfc.FcConfigAppFontAddDir.restype = c_int
            if fonts_dir.exists():
                self.libfc.FcConfigAppFontAddDir(None, str(fonts_dir).encode("utf-8"))

            self.libcairo.cairo_recording_surface_create.argtypes = [c_int, c_void_p]
            self.libcairo.cairo_recording_surface_create.restype = c_void_p
            self.libcairo.cairo_create.argtypes = [c_void_p]
            self.libcairo.cairo_create.restype = c_void_p
            self.libcairo.cairo_copy_path.argtypes = [c_void_p]
            self.libcairo.cairo_copy_path.restype = POINTER(_CairoPath)
            self.libcairo.cairo_path_destroy.argtypes = [POINTER(_CairoPath)]
            self.libcairo.cairo_destroy.argtypes = [c_void_p]
            self.libcairo.cairo_surface_destroy.argtypes = [c_void_p]

            self.libpc.pango_cairo_create_layout.argtypes = [c_void_p]
            self.libpc.pango_cairo_create_layout.restype = c_void_p
            self.libpc.pango_cairo_layout_path.argtypes = [c_void_p, c_void_p]

            self.libpango.pango_font_description_from_string.argtypes = [c_char_p]
            self.libpango.pango_font_description_from_string.restype = c_void_p
            self.libpango.pango_font_description_free.argtypes = [c_void_p]
            self.libpango.pango_layout_set_font_description.argtypes = [c_void_p, c_void_p]
            self.libpango.pango_layout_set_auto_dir.argtypes = [c_void_p, c_int]
            self.libpango.pango_layout_set_text.argtypes = [c_void_p, c_char_p, c_int]
            self.libpango.pango_layout_get_extents.argtypes = [
                c_void_p,
                POINTER(_PangoRectangle),
                POINTER(_PangoRectangle),
            ]
            self.libpango.pango_layout_get_baseline.argtypes = [c_void_p]
            self.libpango.pango_layout_get_baseline.restype = c_int
            self.libgobj.g_object_unref.argtypes = [c_void_p]
            self.available = True
        except OSError:
            self.available = False

    def shape(self, text: str, font_desc: str):
        key = (text, font_desc)
        if key in self._cache:
            return self._cache[key]
        if not self.available:
            return None
        surf = self.libcairo.cairo_recording_surface_create(0x2000, None)
        cr = self.libcairo.cairo_create(surf)
        layout = self.libpc.pango_cairo_create_layout(cr)
        self.libpango.pango_layout_set_auto_dir(layout, 1)
        desc = self.libpango.pango_font_description_from_string(font_desc.encode("utf-8"))
        self.libpango.pango_layout_set_font_description(layout, desc)
        btxt = text.encode("utf-8")
        self.libpango.pango_layout_set_text(layout, btxt, len(btxt))
        ink = _PangoRectangle()
        logical = _PangoRectangle()
        self.libpango.pango_layout_get_extents(layout, byref(ink), byref(logical))
        baseline = self.libpango.pango_layout_get_baseline(layout)
        self.libpc.pango_cairo_layout_path(cr, layout)
        path_ptr = self.libcairo.cairo_copy_path(cr)
        path = path_ptr.contents
        cmds = []
        i = 0
        while i < path.num_data:
            hdr = path.data[i].header
            t = hdr.type
            if t == 0:
                p = path.data[i + 1].point
                cmds.append(f"M{p.x:.1f},{p.y:.1f}")
            elif t == 1:
                p = path.data[i + 1].point
                cmds.append(f"L{p.x:.1f},{p.y:.1f}")
            elif t == 2:
                p1 = path.data[i + 1].point
                p2 = path.data[i + 2].point
                p3 = path.data[i + 3].point
                cmds.append(f"C{p1.x:.1f},{p1.y:.1f} {p2.x:.1f},{p2.y:.1f} {p3.x:.1f},{p3.y:.1f}")
            elif t == 3:
                cmds.append("Z")
            i += hdr.length
        self.libcairo.cairo_path_destroy(path_ptr)
        self.libpango.pango_font_description_free(desc)
        self.libgobj.g_object_unref(layout)
        self.libcairo.cairo_destroy(cr)
        self.libcairo.cairo_surface_destroy(surf)
        P = 1024.0
        result = (
            "".join(cmds),
            (ink.x / P, ink.y / P, ink.width / P, ink.height / P),
            baseline / P,
        )
        self._cache[key] = result
        return result


SHAPER = _ArabicShaper(FONTS_DIR)


def ar_calligraphy(
    text,
    x,
    y,
    size=20,
    fill="#E8AE72",
    font="Aref Ruqaa Bold",
    anchor="end",
    valign="middle",
    cls="",
    style="",
    stroke=None,
    sw=0.4,
    op=1.0,
):
    """Render Arabic text as HarfBuzz-shaped SVG cubic Bezier paths (guaranteed identical everywhere)."""
    shaped = SHAPER.shape(text, f"{font} {size}")
    if shaped and shaped[0]:
        d, (ix, iy, iw, ih), baseline = shaped
        if anchor == "middle":
            tx = x - (ix + iw / 2.0)
        elif anchor == "start":
            tx = x - ix
        else:
            tx = x - (ix + iw)

        if valign == "top":
            ty = y - iy
        elif valign == "bottom":
            ty = y - (iy + ih)
        elif valign == "baseline":
            ty = y - baseline
        else:
            ty = y - (iy + ih / 2.0)

        st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
        cl = f' class="{cls}"' if cls else ""
        stl = f' style="{style}"' if style else ""
        opa = f' opacity="{op}"' if op < 1.0 else ""
        return (
            f'<g transform="translate({tx:.1f},{ty:.1f})"{cl}{stl}{opa} aria-label="{esc(text)}">'
            f'<path d="{d}" fill="{fill}"{st}/></g>'
        )
    # Graceful fallback if libcairo/libpango is absent
    ta = {"start": "start", "middle": "middle", "end": "end"}.get(anchor, "end")
    return (
        f'<text x="{x:.1f}" y="{y + size * 0.3:.1f}" text-anchor="{ta}" '
        f'font-family="{ARAB_FALLBACK}" font-size="{size * 1.2:.1f}" fill="{fill}">{esc(text)}</text>'
    )


def ar_width(text, size=20, font="Aref Ruqaa Bold"):
    shaped = SHAPER.shape(text, f"{font} {size}")
    if shaped and shaped[0]:
        return shaped[1][2]
    return len(text) * size * 0.6


# ---------------------------------------------------------------------------
# Layered GitHub-Safe CSS Animation System
# ---------------------------------------------------------------------------
CSS = """
.a{animation-timing-function:ease-in-out;animation-iteration-count:infinite}
.alt{animation-direction:alternate}
.kb{transform-box:fill-box;transform-origin:50% 45%;animation-name:kb;animation-duration:28s;animation-direction:alternate}
.cbreathe{transform-box:fill-box;transform-origin:50% 48%;animation-name:cbreathe;animation-duration:20s;animation-direction:alternate}
.sway{transform-box:fill-box;transform-origin:50% 0%;animation-name:sway;animation-duration:7.6s;animation-direction:alternate}
.candle{transform-box:fill-box;transform-origin:center;animation-name:candle;animation-duration:3.6s;animation-direction:alternate}
.glint{transform-box:fill-box;transform-origin:center;animation-name:glint;animation-duration:4.4s;animation-direction:alternate}
.spin-cw{transform-box:fill-box;transform-origin:center;animation-name:spin-cw;animation-duration:64s;animation-timing-function:linear}
.spin-ccw{transform-box:fill-box;transform-origin:center;animation-name:spin-ccw;animation-duration:68s;animation-timing-function:linear}
.flow{animation-name:flow;animation-duration:5.5s;animation-timing-function:linear}
.zwave{transform-box:fill-box;transform-origin:center;animation-name:zwave;animation-duration:5.2s;animation-direction:alternate}
.mote{transform-box:fill-box;transform-origin:center;animation-name:mote;animation-duration:8.5s;animation-timing-function:ease-in-out}
.shimmer{animation-name:shimmer;animation-duration:7.5s;animation-timing-function:ease-in-out}
.btn-sheen{animation-name:btn-sheen;animation-duration:5.8s;animation-timing-function:ease-in-out}
.cglow{animation-name:cglow;animation-duration:5s;animation-direction:alternate}
.pulse-dot{animation-name:pulse-dot;animation-duration:2.2s;animation-direction:alternate}
.pulse-ring{transform-box:fill-box;transform-origin:center;animation-name:pulse-ring;animation-duration:2.2s;animation-timing-function:ease-out}
.bead{animation-name:bead;animation-duration:4.2s;animation-timing-function:ease-in-out}
@keyframes kb{0%{transform:scale(1) translateY(0px)}100%{transform:scale(1.065) translateY(-6px)}}
@keyframes cbreathe{0%{transform:scale(1)}100%{transform:scale(1.055)}}
@keyframes sway{0%{transform:rotate(-2.4deg)}100%{transform:rotate(2.4deg)}}
@keyframes candle{0%{opacity:.52;transform:scale(.92)}50%{opacity:.95;transform:scale(1.07)}100%{opacity:.68;transform:scale(.97)}}
@keyframes glint{0%{opacity:.22;transform:scale(.55) rotate(0deg)}55%{opacity:1;transform:scale(1.12) rotate(22deg)}100%{opacity:.3;transform:scale(.68) rotate(45deg)}}
@keyframes spin-cw{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes spin-ccw{from{transform:rotate(360deg)}to{transform:rotate(0deg)}}
@keyframes flow{to{stroke-dashoffset:-48}}
@keyframes zwave{0%{opacity:.62;transform:scale(.95)}100%{opacity:1;transform:scale(1.05)}}
@keyframes mote{0%{opacity:0;transform:translateY(14px) scale(.6)}25%{opacity:.85}75%{opacity:.7}100%{opacity:0;transform:translateY(-22px) scale(1.05)}}
@keyframes shimmer{0%,58%{transform:translateX(-420px)}86%,100%{transform:translateX(460px)}}
@keyframes btn-sheen{0%,62%{transform:translateX(-180px)}92%,100%{transform:translateX(210px)}}
@keyframes cglow{0%{opacity:.86}100%{opacity:1}}
@keyframes pulse-dot{0%{opacity:1}100%{opacity:.45}}
@keyframes pulse-ring{0%{opacity:.85;transform:scale(.9)}100%{opacity:0;transform:scale(2.5)}}
@keyframes bead{0%{opacity:0;transform:translateX(0px)}15%{opacity:1}85%{opacity:1}100%{opacity:0;transform:translateX(var(--dx,120px))}}
@media (prefers-reduced-motion: reduce){.a{animation:none!important}}
"""


def esc(s):
    return html.escape(str(s), quote=False)


def b64_crop(box, size, q=84):
    im = Image.open(SOURCE).convert("RGB").crop(box).resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def svg(W, H, body, title, desc, defs="", animated=True):
    style = f"<style>{CSS}</style>" if animated else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title><desc>{esc(desc)}</desc><defs>{defs}</defs>{style}{body}</svg>"
    )


def save(name, theme, content):
    content = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", content)
    (ASSETS / f"{name}-{theme}.svg").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Authentic Andalusian / Alhambra Architectural Geometry Helpers
# ---------------------------------------------------------------------------
def star8_pts(cx, cy, ro, ratio=0.58):
    pts = []
    for i in range(16):
        a = -math.pi / 2 + i * math.pi / 8
        r = ro if i % 2 == 0 else ro * ratio
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def star8(cx, cy, ro, fill, stroke=None, sw=1.0, op=1.0, ratio=0.58):
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
    opa = f' opacity="{op}"' if op < 1.0 else ""
    return f'<polygon points="{star8_pts(cx, cy, ro, ratio)}" fill="{fill}"{st}{opa}/>'


def khatam_rosette(cx, cy, r, fill1, fill2, gold, ink):
    """Layered Rub el Hizb / 8-fold Andalusian Khatam star rosette."""
    return (
        star8(cx, cy, r, fill1, ink, 0.9, ratio=0.62)
        + star8(cx, cy, r * 0.56, fill2, gold, 0.7, ratio=0.54)
        + f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.19:.1f}" fill="{gold}"/>'
    )


def diamond(cx, cy, r, fill, stroke=None, sw=0.6):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (
        f'<path d="M{cx:.1f},{cy - r:.1f} L{cx + r:.1f},{cy:.1f} '
        f'L{cx:.1f},{cy + r:.1f} L{cx - r:.1f},{cy:.1f} Z" fill="{fill}"{st}/>'
    )


def horseshoe(x, y, W, H, pad=0):
    R0 = W / 1.92
    cx, cy = x + W / 2, y + R0
    R = R0 + pad
    d, ys = 0.96 * R, cy + 0.28 * R
    return (
        f"M{cx - d:.1f},{ys:.1f} A{R:.1f},{R:.1f} 0 1 1 {cx + d:.1f},{ys:.1f} "
        f"V{y + H + pad:.1f} H{cx - d:.1f} Z"
    )


def cordoban_voussoirs(T, x, y, W, H, r_in_pad=2, r_out_pad=19, count=19):
    """Radiating alternating Cordoban polychrome voussoirs around a horseshoe arch."""
    R0 = W / 1.92
    cx, cy = x + W / 2, y + R0
    r_in = R0 + r_in_pad
    r_out = R0 + r_out_pad
    theta0 = math.asin(0.28)
    a_start = math.pi - theta0
    a_end = 2 * math.pi + theta0
    step = (a_end - a_start) / count
    tiles = T["tiles"]
    palette = [tiles[0], tiles[1], T["gold"], tiles[3], tiles[1], tiles[2]]
    out = []
    for i in range(count):
        a0 = a_start + i * step
        a1 = a0 + step
        # Symmetric pattern mirroring from keystone
        sym = min(i, count - 1 - i)
        if i == count // 2:
            fill = f"url(#gold-{T['mode']})"
        else:
            fill = palette[sym % len(palette)]
        x0i, y0i = cx + r_in * math.cos(a0), cy + r_in * math.sin(a0)
        x1i, y1i = cx + r_in * math.cos(a1), cy + r_in * math.sin(a1)
        x0o, y0o = cx + r_out * math.cos(a0), cy + r_out * math.sin(a0)
        x1o, y1o = cx + r_out * math.cos(a1), cy + r_out * math.sin(a1)
        d = (
            f"M{x0i:.1f},{y0i:.1f} L{x0o:.1f},{y0o:.1f} "
            f"A{r_out:.1f},{r_out:.1f} 0 0 1 {x1o:.1f},{y1o:.1f} "
            f"L{x1i:.1f},{y1i:.1f} A{r_in:.1f},{r_in:.1f} 0 0 0 {x0i:.1f},{y0i:.1f} Z"
        )
        out.append(f'<path d="{d}" fill="{fill}" stroke="{T["panel_deep"]}" stroke-width="1" opacity=".92"/>')
    # Side vertical jamb bands below the spring-line, flush to arch pedestal sill
    ys = cy + 0.28 * r_in
    ye = y + H + r_out_pad
    xl_in, xr_in = cx - 0.96 * r_in, cx + 0.96 * r_in
    xl_out, xr_out = cx - 0.96 * r_out, cx + 0.96 * r_out
    band_h = max(1, (ye - ys))
    segs = max(5, int(band_h / 24))
    sh = band_h / segs
    for k in range(segs):
        yy = ys + k * sh
        col = tiles[k % 4] if k % 2 == 0 else T["panel2"]
        out.append(
            f'<rect x="{xl_out:.1f}" y="{yy:.1f}" width="{xl_in - xl_out:.1f}" height="{sh:.1f}" '
            f'fill="{col}" stroke="{T["panel_deep"]}" stroke-width="0.8" opacity=".88"/>'
        )
        out.append(
            f'<rect x="{xr_in:.1f}" y="{yy:.1f}" width="{xr_out - xr_in:.1f}" height="{sh:.1f}" '
            f'fill="{col}" stroke="{T["panel_deep"]}" stroke-width="0.8" opacity=".88"/>'
        )
    # Clean gilded sill plinth across bottom of horseshoe arch
    out.append(
        f'<rect x="{xl_out:.1f}" y="{y + H + 2:.1f}" width="{xr_out - xl_out:.1f}" height="{r_out_pad - 2:.1f}" '
        f'fill="{T["panel"]}" stroke="url(#gold-{T["mode"]})" stroke-width="1"/>'
    )
    out.append(
        f'<line x1="{xl_in:.1f}" y1="{y + H + r_out_pad / 2 + 1:.1f}" x2="{xr_in:.1f}" y2="{y + H + r_out_pad / 2 + 1:.1f}" '
        f'stroke="{T["gold"]}" stroke-width="0.8" stroke-dasharray="6 4" opacity=".65"/>'
    )
    return "".join(out)


def polylobed_trim(T, x, y, W, lobes=15, pad=-1.5):
    """Delicate multifoil / scalloped gold inner arch cusps (Aljafería / Córdoba)."""
    R0 = W / 1.92
    cx, cy = x + W / 2, y + R0
    R = R0 + pad
    theta0 = math.asin(0.28)
    a_start = math.pi - theta0 + 0.05
    a_end = 2 * math.pi + theta0 - 0.05
    step = (a_end - a_start) / lobes
    pts = []
    for i in range(lobes):
        a0 = a_start + i * step
        a1 = a0 + step
        am = (a0 + a1) / 2
        x0, y0 = cx + R * math.cos(a0), cy + R * math.sin(a0)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        xm, ym = cx + (R - 7.5) * math.cos(am), cy + (R - 7.5) * math.sin(am)
        if i == 0:
            pts.append(f"M{x0:.1f},{y0:.1f}")
        pts.append(f"Q{xm:.1f},{ym:.1f} {x1:.1f},{y1:.1f}")
    return f'<path d="{" ".join(pts)}" fill="none" stroke="{T["gold_hi"]}" stroke-width="1.35" opacity=".82"/>'


def stepped_merlons(x, y, w, n, h=14):
    """Authentic stepped Almohad / Alhambra crenellated merlons."""
    u = w / n
    s1 = h * 0.42
    s2 = h * 0.74
    d = f"M{x:.1f},{y + h:.1f}"
    for i in range(n):
        x0 = x + i * u
        d += (
            f" H{x0 + u * 0.16:.1f} V{y + s2:.1f}"
            f" H{x0 + u * 0.30:.1f} V{y + s1:.1f}"
            f" L{x0 + u * 0.50:.1f},{y:.1f}"
            f" L{x0 + u * 0.70:.1f},{y + s1:.1f}"
            f" H{x0 + u * 0.84:.1f} V{y + s2:.1f}"
            f" H{x0 + u:.1f} V{y + h:.1f}"
        )
    return d


def frieze(T, x0, x1, y, h, phase=0, wave=False):
    """Double-railed Andalusian 8-fold zellige star frieze with golden diamonds."""
    step = h * 1.38
    n = max(1, int((x1 - x0) / step))
    off = (x1 - x0 - n * step) / 2 + step / 2
    cy = y + h / 2
    tiles = T["tiles"]
    out = [
        f'<line x1="{x0}" y1="{y - 2:.1f}" x2="{x1}" y2="{y - 2:.1f}" stroke="{T["gold"]}" stroke-width="0.9" opacity=".55"/>',
        f'<line x1="{x0}" y1="{y + h + 2:.1f}" x2="{x1}" y2="{y + h + 2:.1f}" stroke="{T["gold"]}" stroke-width="0.9" opacity=".55"/>',
        f'<line x1="{x0}" y1="{cy:.1f}" x2="{x1}" y2="{cy:.1f}" stroke="{T["gold"]}" stroke-width="0.8" opacity=".4"/>',
    ]
    for i in range(n):
        cx = x0 + off + i * step
        cls = ' class="zwave a"' if wave else ""
        style = f' style="animation-delay:{-(i * 0.35):.2f}s"' if wave else ""
        c1 = tiles[(i + phase) % 4]
        c2 = tiles[(i + phase + 2) % 4]
        out.append(f"<g{cls}{style}>{khatam_rosette(cx, cy, h * 0.48, c1, c2, T['gold_hi'], T['ink'])}</g>")
        if i < n - 1:
            out.append(diamond(cx + step / 2, cy, h * 0.16, T["gold"], T["panel_deep"], 0.4))
    return "".join(out)


def muqarnas_vault(T, x0, x1, y, tiers=3):
    """Three-dimensional shaded Alhambra muqarnas honeycomb stalactite vaulting."""
    out = []
    w, h = 46, 36
    tiles = T["tiles"]
    for t in range(tiers):
        cnt = int((x1 - x0) / w) + 2
        for i in range(cnt):
            x = x0 + i * w - (w / 2 if t % 2 else 0)
            yy = y + t * 21
            # Outer pointed niche
            d_outer = (
                f"M{x:.1f},{yy:.1f} "
                f"C{x:.1f},{yy + h * 0.68:.1f} {x + w * 0.34:.1f},{yy + h * 0.88:.1f} {x + w * 0.5:.1f},{yy + h:.1f} "
                f"C{x + w * 0.66:.1f},{yy + h * 0.88:.1f} {x + w:.1f},{yy + h * 0.68:.1f} {x + w:.1f},{yy:.1f} Z"
            )
            # Inner recessed shadow niche
            pad = 6.5
            d_inner = (
                f"M{x + pad:.1f},{yy + 2:.1f} "
                f"C{x + pad:.1f},{yy + h * 0.56:.1f} {x + w * 0.39:.1f},{yy + h * 0.72:.1f} {x + w * 0.5:.1f},{yy + h * 0.82:.1f} "
                f"C{x + w * 0.61:.1f},{yy + h * 0.72:.1f} {x + w - pad:.1f},{yy + h * 0.56:.1f} {x + w - pad:.1f},{yy + 2:.1f} Z"
            )
            cidx = (i + t) % 4
            out.append(
                f'<path d="{d_outer}" fill="url(#muq{cidx})" stroke="{T["gold"]}" stroke-width="0.95" opacity="{0.96 - t * 0.06:.2f}"/>'
            )
            out.append(
                f'<path d="{d_inner}" fill="{T["muq_shade"]}" opacity="{0.36 + t * 0.06:.2f}"/>'
            )
            # Delicate gold highlight drop at bottom cusp
            out.append(
                f'<circle cx="{x + w * 0.5:.1f}" cy="{yy + h - 3.5:.1f}" r="1.4" fill="{T["gold_hi"]}" opacity=".75"/>'
            )
    return "".join(out)


def fanous_lantern(T, x, y_top, scale=1.0, delay=0.0):
    """Hanging Andalusian pierced brass lantern with gentle sway & warm candlelight."""
    s = scale
    # Coordinates relative to top anchor (0, 0)
    chain_len = 22 * s
    cap_y = chain_len
    body_top = cap_y + 11 * s
    body_bot = body_top + 28 * s
    w = 13 * s
    glow_y = (body_top + body_bot) / 2
    return (
        f'<g transform="translate({x:.1f},{y_top:.1f})">'
        f'<g class="sway a" style="animation-delay:{delay:.1f}s">'
        # Warm candlelight aura
        f'<circle class="candle a" style="animation-delay:{delay - 1.1:.1f}s" cx="0" cy="{glow_y:.1f}" r="{34 * s:.1f}" fill="url(#lantern-glow)"/>'
        # Chain
        f'<line x1="0" y1="0" x2="0" y2="{chain_len:.1f}" stroke="{T["gold"]}" stroke-width="{1.2 * s:.2f}" stroke-dasharray="2.5 2"/>'
        f'<circle cx="0" cy="{chain_len:.1f}" r="{2.2 * s:.1f}" fill="{T["gold_hi"]}"/>'
        # Pointed Andalusian dome cap
        f'<path d="M0,{cap_y - 3 * s:.1f} Q{w * 0.85:.1f},{cap_y + 4 * s:.1f} {w:.1f},{body_top:.1f} '
        f'H{-w:.1f} Q{-w * 0.85:.1f},{cap_y + 4 * s:.1f} 0,{cap_y - 3 * s:.1f} Z" '
        f'fill="url(#gold-{T["mode"]})" stroke="{T["gold_lo"]}" stroke-width="0.8"/>'
        # Lantern body frame
        f'<path d="M{-w:.1f},{body_top:.1f} L{-w * 0.82:.1f},{body_bot:.1f} H{w * 0.82:.1f} L{w:.1f},{body_top:.1f} Z" '
        f'fill="{T["panel_deep"]}" stroke="{T["gold"]}" stroke-width="1.2"/>'
        # Illuminated arch window inside lantern
        f'<path class="candle a" style="animation-delay:{delay - 0.5:.1f}s" '
        f'd="M{-w * 0.52:.1f},{body_bot - 3 * s:.1f} V{body_top + 9 * s:.1f} '
        f'Q0,{body_top + 1 * s:.1f} {w * 0.52:.1f},{body_top + 9 * s:.1f} V{body_bot - 3 * s:.1f} Z" '
        f'fill="{T["warm"]}" opacity=".9"/>'
        # Filigree center rib
        f'<line x1="0" y1="{body_top:.1f}" x2="0" y2="{body_bot:.1f}" stroke="{T["gold_lo"]}" stroke-width="0.8" opacity=".75"/>'
        # Bottom finial spire
        f'<path d="M{-w * 0.72:.1f},{body_bot:.1f} L0,{body_bot + 10 * s:.1f} L{w * 0.72:.1f},{body_bot:.1f} Z" '
        f'fill="url(#gold-{T["mode"]})"/>'
        f'<circle cx="0" cy="{body_bot + 12.5 * s:.1f}" r="{1.7 * s:.1f}" fill="{T["gold_hi"]}"/>'
        f"</g></g>"
    )


def arabesque_bracket(T, x, y, direction=1, size=1.0):
    """Delicate Andalusian calligraphic bracket flourish (direction: +1 left, -1 right)."""
    d = direction
    s = size
    return (
        f'<g transform="translate({x:.1f},{y:.1f}) scale({d * s:.2f},{s:.2f})">'
        f'<path d="M0,0 C8,-9 18,-9 25,-3 C19,-1 15,0 25,3 C18,9 8,9 0,0 Z" '
        f'fill="none" stroke="{T["gold"]}" stroke-width="1.25" opacity=".85"/>'
        f'<circle cx="11" cy="0" r="2.2" fill="{T["gold_hi"]}"/>'
        f'<path d="M27,0 H48" stroke="{T["gold"]}" stroke-width="0.9" opacity=".6"/>'
        f'<circle cx="51" cy="0" r="1.6" fill="{T["gold"]}"/>'
        f"</g>"
    )


def zellige_pattern(T, pid):
    """Authentic 8-fold Alhambra Khatam & Cross seamless tilework pattern."""
    c = T["line"]
    return (
        f'<pattern id="{pid}" width="64" height="64" patternUnits="userSpaceOnUse">'
        # Interlocking Rub el Hizb 8-point star centered at (32, 32)
        f'<rect x="14" y="14" width="36" height="36" fill="none" stroke="{c}" stroke-width="0.75"/>'
        f'<rect x="14" y="14" width="36" height="36" transform="rotate(45 32 32)" fill="none" stroke="{c}" stroke-width="0.75"/>'
        # Corner quarter-stars connecting tiles seamlessly
        f'<path d="M0,12 L12,0 M52,0 L64,12 M64,52 L52,64 M12,64 L0,52" stroke="{c}" stroke-width="0.65"/>'
        f'<polygon points="{star8_pts(32, 32, 11, 0.55)}" fill="none" stroke="{c}" stroke-width="0.65"/>'
        f'<circle cx="32" cy="32" r="2.4" fill="none" stroke="{c}" stroke-width="0.7"/>'
        f"</pattern>"
    )


def shared_defs(T, sid):
    """Metallic gold gradients, warm candlelight glow, shimmer gradient, and tile pattern."""
    mode = T["mode"]
    tiles = T["tiles"]
    muq_grads = []
    for i, col in enumerate(tiles):
        muq_grads.append(
            f'<linearGradient id="muq{i}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{col}" stop-opacity=".95"/>'
            f'<stop offset="1" stop-color="{T["panel_deep"]}" stop-opacity=".92"/>'
            f"</linearGradient>"
        )
    return (
        f'<linearGradient id="{sid}g" x1="0" y1="0" x2="0.2" y2="1">'
        f'<stop offset="0" stop-color="{T["bg"]}"/>'
        f'<stop offset="0.52" stop-color="{T["bg_mid"]}"/>'
        f'<stop offset="1" stop-color="{T["bg2"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="gold-{mode}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{T["gold_hi"]}"/>'
        f'<stop offset="0.48" stop-color="{T["gold"]}"/>'
        f'<stop offset="1" stop-color="{T["gold_lo"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="callig-{mode}" x1="0" y1="0" x2="1" y2="0.4">'
        f'<stop offset="0" stop-color="{T["gold_hi"] if mode == "dark" else T["accent"]}"/>'
        f'<stop offset="0.5" stop-color="{T["accent"] if mode == "dark" else T["gold_lo"]}"/>'
        f'<stop offset="1" stop-color="{T["gold"] if mode == "dark" else T["accent"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="panel-{mode}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{T["panel"]}"/>'
        f'<stop offset="1" stop-color="{T["panel2"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="sheen-{mode}" x1="0" y1="0" x2="1" y2="0.3">'
        f'<stop offset="0" stop-color="{T["gold_hi"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{T["gold_hi"]}" stop-opacity="{0.26 if mode == "dark" else 0.34}"/>'
        f'<stop offset="1" stop-color="{T["gold_hi"]}" stop-opacity="0"/>'
        f"</linearGradient>"
        f'<radialGradient id="lantern-glow" cx=".5" cy=".5" r=".5">'
        f'<stop offset="0" stop-color="{T["warm"]}" stop-opacity="{0.42 if mode == "dark" else 0.28}"/>'
        f'<stop offset="0.55" stop-color="{T["warm"]}" stop-opacity="{0.14 if mode == "dark" else 0.08}"/>'
        f'<stop offset="1" stop-color="{T["warm"]}" stop-opacity="0"/>'
        f"</radialGradient>"
        + "".join(muq_grads)
        + zellige_pattern(T, sid + "t")
    )


def base(T, W, H, sid="s"):
    defs = shared_defs(T, sid)
    body = (
        f'<rect width="{W}" height="{H}" fill="url(#{sid}g)"/>'
        f'<rect width="{W}" height="{H}" fill="url(#{sid}t)" opacity="{T["tile_op"]}"/>'
    )
    return defs, body


def star_twinkle(x, y, s, T, delay=0.0):
    return (
        f'<g transform="translate({x:.1f},{y:.1f}) scale({s})">'
        f'<path class="glint a" style="animation-delay:{delay:.1f}s" fill="{T["star"]}" '
        f'd="M0,-12 L2.2,-2.2 L12,0 L2.2,2.2 L0,12 L-2.2,2.2 L-12,0 L-2.2,-2.2 Z"/>'
        f"</g>"
    )


def floating_mote(x, y, r, T, delay=0.0, dur=8.5):
    return (
        f'<circle class="mote a" style="animation-delay:{delay:.1f}s;animation-duration:{dur:.1f}s" '
        f'cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{T["gold_hi"]}"/>'
    )


def panel(T, x, y, w, h, n):
    """Stepped-merlon crowned Alhambra architectural panel with double alfiz frame."""
    d = stepped_merlons(x, y, w, n, 14) + f" V{y + h} H{x} Z"
    tiles = T["tiles"]
    return (
        # Soft drop shadow behind panel
        f'<path d="{d}" transform="translate(0,4)" fill="#000000" opacity="{T["shadow_op"]}"/>'
        # Panel body
        f'<path d="{d}" fill="url(#panel-{T["mode"]})" stroke="url(#gold-{T["mode"]})" stroke-width="2" stroke-linejoin="round"/>'
        # Inner alfiz hairline frame
        f'<rect x="{x + 9}" y="{y + 21}" width="{w - 18}" height="{h - 30}" fill="none" stroke="{T["gold"]}" stroke-width="0.9" opacity=".55"/>'
        f'<rect x="{x + 13}" y="{y + 25}" width="{w - 26}" height="{h - 38}" fill="none" stroke="{T["gold"]}" stroke-width="0.5" opacity=".32"/>'
        # Corner Khatam micro-rosettes
        + star8(x + 16, y + h - 16, 6, tiles[0], T["gold"], 0.6)
        + star8(x + w - 16, y + h - 16, 6, tiles[1], T["gold"], 0.6)
        # Animated top zellige frieze
        + frieze(T, x + 22, x + w - 22, y + 30, 18, 0, wave=True)
    )


def heading(x, y, text, ar_text, ar_right, T, size=27, ar_size=20):
    """Bilingual Alhambra heading: Khatam crest + Serif title + Vectorized Aref Ruqaa calligraphy."""
    tiles = T["tiles"]
    return (
        khatam_rosette(x + 12, y - 9, 12, tiles[1], tiles[0], T["gold_hi"], T["ink"])
        + f'<text x="{x + 34}" y="{y}" font-family="{SERIF}" font-size="{size}" letter-spacing="0.6" fill="{T["ink"]}">{esc(text)}</text>'
        + ar_calligraphy(
            ar_text,
            ar_right,
            y - 8,
            size=ar_size,
            fill=f"url(#callig-{T['mode']})",
            font="Aref Ruqaa Bold",
            anchor="end",
            valign="middle",
            cls="cglow a",
        )
    )


# ---------------------------------------------------------------------------
# 1. HERO SECTION (900 x 630)
# ---------------------------------------------------------------------------
def hero(T, imgs):
    W, H = 900, 630
    defs, bg = base(T, W, H, "h")
    ax, ay, aw, ah = 536, 72, 298, 456
    alfiz_x, alfiz_y, alfiz_w, alfiz_h = 502, 34, 366, 514
    cx_arch = ax + aw / 2

    defs += (
        f'<clipPath id="hclip"><path d="{horseshoe(ax, ay, aw, ah)}"/></clipPath>'
        f'<clipPath id="hframe-clip"><path d="{horseshoe(ax, ay, aw, ah, 20)}"/></clipPath>'
        f'<clipPath id="hav"><circle cx="64" cy="36" r="14"/></clipPath>'
        f'<radialGradient id="hglow" cx=".5" cy=".48" r=".52">'
        f'<stop offset="0" stop-color="{T["glow"]}" stop-opacity="{0.42 if T["mode"] == "dark" else 0.25}"/>'
        f'<stop offset="0.6" stop-color="{T["warm"]}" stop-opacity="{0.14 if T["mode"] == "dark" else 0.08}"/>'
        f'<stop offset="1" stop-color="{T["glow"]}" stop-opacity="0"/>'
        f"</radialGradient>"
        f'<radialGradient id="hvig" cx=".5" cy=".45" r=".62">'
        f'<stop offset="0.65" stop-color="#000000" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#040D0C" stop-opacity="{0.45 if T["mode"] == "dark" else 0.2}"/>'
        f"</radialGradient>"
    )

    s = [
        bg,
        # Ambient courtyard glow behind the Alhambra arch
        f'<ellipse cx="{cx_arch:.1f}" cy="{ay + ah / 2:.1f}" rx="290" ry="300" fill="url(#hglow)"/>',
        # Outer gilded border frame
        f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" fill="none" stroke="{T["gold"]}" stroke-width="1.1" opacity=".45"/>',
        # Top handle bar
        f'<image href="{imgs[1]}" x="50" y="22" width="28" height="28" clip-path="url(#hav)" preserveAspectRatio="xMidYMid slice"/>',
        f'<circle cx="64" cy="36" r="14.5" fill="none" stroke="url(#gold-{T["mode"]})" stroke-width="1.8"/>',
        f'<text x="88" y="40.5" font-family="{MONO}" font-size="12" letter-spacing="0.4" fill="{T["soft"]}">{esc(HANDLE)}  /  README</text>',
        # Subtle gilded rule with central Khatam jewel
        f'<line x1="50" y1="64" x2="444" y2="64" stroke="url(#gold-{T["mode"]})" stroke-width="1.2" opacity=".8"/>',
        khatam_rosette(247, 64, 9, T["tiles"][1], T["tiles"][0], T["gold_hi"], T["ink"]),
        diamond(50, 64, 3.2, T["gold"]),
        diamond(444, 64, 3.2, T["gold"]),
    ]

    # Greeting + Royal Arabic Calligraphic Name Signature
    s.append(f'<text x="52" y="114" font-family="{SERIF}" font-size="18.5" font-style="italic" fill="{T["soft"]}">Hi, I\'m</text>')
    # Ornamental calligraphic cartouche for Solayman El Mouden in Arabic on the right of "Hi, I'm"
    ar_name_w = ar_width(AR["name"], size=24, font="Aref Ruqaa Bold")
    s.append(arabesque_bracket(T, 448 - ar_name_w - 64, 108, direction=1, size=0.82))
    s.append(
        ar_calligraphy(
            AR["name"],
            446,
            108,
            size=24,
            fill=f"url(#callig-{T['mode']})",
            font="Aref Ruqaa Bold",
            anchor="end",
            valign="middle",
            cls="cglow a",
        )
    )

    # Monumental Display Name
    for txt, y in ((NAME_1, 184), (NAME_2, 248)):
        s.append(
            f'<text x="54.5" y="{y + 3}" font-family="{SERIF}" font-size="60" letter-spacing="0.8" '
            f'fill="{T["tiles"][0]}" opacity="{0.45 if T["mode"] == "dark" else 0.22}">{esc(txt)}</text>'
        )
        s.append(
            f'<text x="52" y="{y}" font-family="{SERIF}" font-size="60" letter-spacing="0.8" fill="{T["ink"]}">{esc(txt)}</text>'
        )

    # Bilingual Role Cartouche Ribbon
    s.append(
        f'<rect x="52" y="276" width="424" height="44" rx="6" fill="{T["panel"]}" fill-opacity=".78" '
        f'stroke="url(#gold-{T["mode"]})" stroke-width="1.2"/>'
    )
    s.append(
        f'<rect x="56" y="280" width="416" height="36" rx="4" fill="none" stroke="{T["gold"]}" stroke-width="0.5" opacity=".45"/>'
    )
    s.append(
        f'<text x="72" y="303" font-family="{SANS}" font-size="13" font-weight="700" letter-spacing="4.0" fill="{T["accent"]}">{esc(ROLE)}</text>'
    )
    s.append(star8(324, 298, 6.5, T["tiles"][1], T["gold_hi"], 0.6))
    s.append(
        ar_calligraphy(
            AR["role"],
            460,
            297,
            size=17.5,
            fill=f"url(#callig-{T['mode']})",
            font="Aref Ruqaa Bold",
            anchor="end",
            valign="middle",
            cls="cglow a",
        )
    )

    # Pillars with gilded star dividers
    s.append(
        f'<text x="54" y="358" font-family="{SERIF}" font-size="17.5" font-style="italic" fill="{T["ink"]}">'
        f'{esc("  ✦  ".join(PILLARS))}</text>'
    )

    # Tagline
    for i, line in enumerate(TAGLINE):
        s.append(f'<text x="54" y="{398 + i * 24}" font-family="{SERIF}" font-size="15.5" fill="{T["soft"]}">{esc(line)}</text>')

    # Status & Location architectural pill in lower-left courtyard
    s.append(
        f'<rect x="54" y="486" width="320" height="32" rx="16" fill="{T["panel"]}" fill-opacity=".85" '
        f'stroke="{T["gold"]}" stroke-width="1" stroke-opacity=".6"/>'
    )
    s.append(f'<circle class="pulse-ring a" cx="73" cy="502" r="4" fill="none" stroke="{T["live"]}" stroke-width="1.2"/>')
    s.append(f'<circle class="pulse-dot a" cx="73" cy="502" r="3.4" fill="{T["live"]}"/>')
    s.append(
        f'<text x="86" y="506" font-family="{MONO}" font-size="11" fill="{T["ink"]}">'
        f'{esc(STATUS)}  ·  {esc(LOCATION)}</text>'
    )

    # Hanging swaying brass lantern accent on upper-left of the alfiz
    s.append(fanous_lantern(T, 474, 10, scale=0.82, delay=-1.2))

    # --- RIGHT COLUMN: CORDOBAN ALFIZ + HORSESHOE ARCH ---
    # Outer Alfiz rectangular frame
    s.append(
        f'<rect x="{alfiz_x}" y="{alfiz_y}" width="{alfiz_w}" height="{alfiz_h}" rx="4" '
        f'fill="{T["panel_deep"]}" fill-opacity=".55" stroke="url(#gold-{T["mode"]})" stroke-width="2"/>'
    )
    s.append(
        f'<rect x="{alfiz_x + 7}" y="{alfiz_y + 7}" width="{alfiz_w - 14}" height="{alfiz_h - 14}" '
        f'fill="none" stroke="{T["gold"]}" stroke-width="0.8" opacity=".55"/>'
    )

    # Spandrel 8-fold zellige rosettes in upper-left & upper-right corners of alfiz
    for sx, sy, ph in ((alfiz_x + 34, alfiz_y + 34, 0), (alfiz_x + alfiz_w - 34, alfiz_y + 34, 2)):
        s.append(
            f'<g class="spin-{"cw" if ph == 0 else "ccw"} a">'
            f'<polygon points="{star8_pts(sx, sy, 21, 0.78)}" fill="none" stroke="{T["gold"]}" stroke-width="0.9" stroke-dasharray="3 3" opacity=".75"/>'
            f"</g>"
        )
        s.append(khatam_rosette(sx, sy, 14, T["tiles"][ph], T["tiles"][(ph + 1) % 4], T["gold_hi"], T["ink"]))

    # Radiating Cordoban polychrome voussoirs
    s.append(cordoban_voussoirs(T, ax, ay, aw, ah, r_in_pad=2, r_out_pad=20, count=19))
    s.append(f'<path d="{horseshoe(ax, ay, aw, ah, 21)}" fill="none" stroke="url(#gold-{T["mode"]})" stroke-width="2"/>')
    s.append(f'<path d="{horseshoe(ax, ay, aw, ah, 2)}" fill="none" stroke="url(#gold-{T["mode"]})" stroke-width="1.6"/>')

    # Clipped hero artwork with slow Ken Burns breathing + subtle inner vignette + shimmer sweep
    s.append(
        f'<g clip-path="url(#hclip)">'
        f'<image class="kb a" href="{imgs["hero"]}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" preserveAspectRatio="xMidYMid slice"/>'
        f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="url(#hvig)"/>'
        f'<rect class="shimmer a" x="{ax}" y="{ay - 40}" width="110" height="{ah + 80}" '
        f'transform="skewX(-20)" fill="url(#sheen-{T["mode"]})"/>'
        f"</g>"
    )

    # Delicate multifoil polylobed inner arch trim
    s.append(polylobed_trim(T, ax, ay, aw, lobes=15, pad=-1.5))
    s.append(f'<path d="{horseshoe(ax, ay, aw, ah)}" fill="none" stroke="{T["ink"]}" stroke-width="1.3" opacity=".8"/>')

    # Crowning Astrolabe Keystone Crest above arch
    crest_y = alfiz_y
    s.append(
        f'<g class="spin-cw a">'
        f'<polygon points="{star8_pts(cx_arch, crest_y, 20, 0.76)}" fill="none" stroke="{T["gold_hi"]}" stroke-width="1" stroke-dasharray="3 4"/>'
        f"</g>"
    )
    s.append(khatam_rosette(cx_arch, crest_y, 13, T["tiles"][1], T["tiles"][0], T["gold_hi"], T["ink"]))
    s.append(star_twinkle(cx_arch, crest_y, 0.75, T, delay=-0.5))

    # Floating golden starlight motes & celestial twinkles around courtyard
    s.append(star_twinkle(492, 165, 0.52, T, delay=-1.8))
    s.append(star_twinkle(876, 138, 0.58, T, delay=-3.1))
    s.append(star_twinkle(872, 412, 0.45, T, delay=-0.9))
    for mx, my, mr, md, dur in (
        (488, 280, 1.9, -1.0, 7.8),
        (498, 430, 1.6, -4.2, 9.2),
        (874, 240, 2.0, -2.5, 8.4),
        (878, 355, 1.5, -5.8, 7.2),
        (445, 520, 1.7, -3.4, 8.8),
    ):
        s.append(floating_mote(mx, my, mr, T, delay=md, dur=dur))

    # Artwork caption inside bottom margin of alfiz
    s.append(
        f'<text x="{cx_arch:.1f}" y="{alfiz_y + alfiz_h + 17}" text-anchor="middle" '
        f'font-family="{SANS}" font-size="10.2" letter-spacing="0.4" fill="{T["muted"]}">{esc(ART_CAPTION)}</text>'
    )

    # Bottom Alhambra Zellige Star Frieze with sunlight wave
    s.append(frieze(T, 16, W - 16, H - 38, 22, 1, wave=True))

    return svg(W, H, "".join(s), f"{FULL_NAME}: {ROLE.title()}", "Alhambra Cordoban horseshoe-arch profile header.", defs)


# ---------------------------------------------------------------------------
# 2. BUTTONS (160 x 44 — Ornate Andalusian Cartouche Medallions)
# ---------------------------------------------------------------------------
def button(T, label, delay=0.0):
    W, H = 160, 44
    mode = T["mode"]
    outer = f"M18,3 H{W - 18} L{W - 4},22 L{W - 18},{H - 3} H18 L4,22 Z"
    inner = f"M21,7 H{W - 21} L{W - 9},22 L{W - 21},{H - 7} H21 L9,22 Z"
    defs = (
        f'<linearGradient id="bg-{mode}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{T["btn"]}"/>'
        f'<stop offset="1" stop-color="{T["btn2"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="gd-{mode}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{T["gold_hi"]}"/>'
        f'<stop offset="0.5" stop-color="{T["gold"]}"/>'
        f'<stop offset="1" stop-color="{T["gold_lo"]}"/>'
        f"</linearGradient>"
        f'<linearGradient id="bsheen" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#FFF5D6" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="#FFF5D6" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="#FFF5D6" stop-opacity="0"/>'
        f"</linearGradient>"
        f'<clipPath id="bclip"><path d="{outer}"/></clipPath>'
    )
    body = (
        f'<path d="{outer}" fill="url(#bg-{mode})" stroke="url(#gd-{mode})" stroke-width="1.8" stroke-linejoin="round"/>'
        f'<path d="{inner}" fill="none" stroke="{T["gold_hi"]}" stroke-width="0.7" opacity=".5"/>'
        f'<g clip-path="url(#bclip)">'
        f'<rect class="btn-sheen a" style="animation-delay:{delay:.1f}s" x="0" y="-6" width="52" height="56" transform="skewX(-22)" fill="url(#bsheen)"/>'
        f"</g>"
        + star8(26, 22, 7.5, T["gold_hi"], T["btn2"], 0.6)
        + star8(W - 26, 22, 4.5, T["gold_hi"], None, 0, op=0.8)
        + f'<text x="{W / 2 + 2:.0f}" y="27.2" text-anchor="middle" font-family="{SERIF}" font-size="15" font-weight="700" letter-spacing="0.9" fill="{T["btntxt"]}">{esc(label)}</text>'
    )
    return svg(W, H, body, label, f"Andalusian cartouche button linking to {label}", defs, animated=True)


# ---------------------------------------------------------------------------
# 3. ABOUT & JOURNEY PANEL (900 x 430)
# ---------------------------------------------------------------------------
def about(T):
    W, H = 900, 430
    defs, bg = base(T, W, H, "a")
    s = [bg, panel(T, 18, 14, 864, 398, 22)]
    s.append(heading(50, 104, "About", AR["about"], 452, T, size=27, ar_size=21))
    s.append(heading(516, 104, "My journey", AR["journey"], 852, T, size=27, ar_size=21))

    # Subtle gilded sub-lines under both headings
    s.append(f'<line x1="50" y1="118" x2="452" y2="118" stroke="{T["gold"]}" stroke-width="0.8" opacity=".4"/>')
    s.append(f'<line x1="516" y1="118" x2="852" y2="118" stroke="{T["gold"]}" stroke-width="0.8" opacity=".4"/>')

    # Left: About bio
    lines = textwrap.wrap(ABOUT, 50)
    for i, line in enumerate(lines):
        s.append(f'<text x="52" y="{148 + i * 24}" font-family="{SERIF}" font-size="14.6" fill="{T["ink"]}">{esc(line)}</text>')

    # Illuminated callout strip for facts & focus
    y_box = 148 + 24 * len(lines) + 18
    fact_lines = textwrap.wrap(FACTS, 54)
    box_h = 18 * len(fact_lines) + 42
    s.append(
        f'<rect x="52" y="{y_box}" width="400" height="{box_h}" rx="6" fill="{T["panel_deep"]}" fill-opacity=".62" '
        f'stroke="{T["gold"]}" stroke-width="0.8" stroke-opacity=".45"/>'
    )
    s.append(f'<rect x="52" y="{y_box}" width="4" height="{box_h}" rx="2" fill="url(#gold-{T["mode"]})"/>')
    yy = y_box + 20
    for line in fact_lines:
        s.append(f'<text x="66" y="{yy}" font-family="{SANS}" font-size="12" fill="{T["soft"]}">{esc(line)}</text>')
        yy += 18
    s.append(
        f'<text x="66" y="{yy + 9}" font-family="{SANS}" font-size="12.5" font-weight="700" fill="{T["accent"]}">'
        f"✦  {esc(FOCUS)}</text>"
    )

    # Ornamental center divider column
    s.append(f'<line x1="486" y1="82" x2="486" y2="378" stroke="url(#gold-{T["mode"]})" stroke-width="1.3" opacity=".75"/>')
    for k, cy in enumerate((136, 230, 324)):
        s.append(khatam_rosette(486, cy, 8.5, T["tiles"][(k + 1) % 4], T["tiles"][k % 4], T["gold_hi"], T["ink"]))
    s.append(star_twinkle(486, 230, 0.55, T, delay=-1.4))

    # Right: Journey paths with animated flowing lines + gliding golden beads + domain pills
    tiles = T["tiles"]
    for i, (lang, area) in enumerate(JOURNEY):
        ry = 158 + i * 48
        pill_w = max(92, len(area) * 7.8 + 24)
        pill_x = 852 - pill_w
        x1 = 516 + len(lang) * 9.8 + 16
        x2 = pill_x - 14
        dx = max(24, x2 - x1)
        col = tiles[i % 4]

        s.append(f'<text x="516" y="{ry + 5}" font-family="{SERIF}" font-size="17.5" fill="{T["ink"]}">{esc(lang)}</text>')
        # Soft track rail
        s.append(f'<line x1="{x1:.0f}" y1="{ry}" x2="{x2:.0f}" y2="{ry}" stroke="{col}" stroke-width="1.5" opacity=".25"/>')
        # Flowing dashed stream
        s.append(
            f'<line class="flow a" style="animation-delay:{-i * 0.7:.1f}s" x1="{x1:.0f}" y1="{ry}" x2="{x2:.0f}" y2="{ry}" '
            f'stroke="{col}" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="3 9"/>'
        )
        # Gliding golden light bead
        s.append(
            f'<circle class="bead a" style="--dx:{dx:.0f}px;animation-delay:{-i * 0.85:.2f}s" '
            f'cx="{x1:.0f}" cy="{ry}" r="3.2" fill="{T["gold_hi"]}"/>'
        )
        s.append(diamond(x2 + 4, ry, 4.2, T["gold"], T["panel_deep"], 0.6))
        # Domain pill badge
        s.append(
            f'<rect x="{pill_x:.1f}" y="{ry - 13}" width="{pill_w:.1f}" height="26" rx="13" '
            f'fill="{T["panel_deep"]}" fill-opacity=".82" stroke="{col}" stroke-width="1.1" stroke-opacity=".85"/>'
        )
        s.append(
            f'<text x="{pill_x + pill_w / 2:.1f}" y="{ry + 4.5}" text-anchor="middle" '
            f'font-family="{SANS}" font-size="12" font-weight="700" fill="{T["accent"]}">{esc(area)}</text>'
        )

    return svg(W, H, "".join(s), "About and journey", "About and engineering journey.", defs)


# ---------------------------------------------------------------------------
# 4. TECHNOLOGIES & SKILLS PANEL (900 x 456)
# ---------------------------------------------------------------------------
def skills(T):
    W, H = 900, 456
    defs, bg = base(T, W, H, "k")
    s = [
        bg,
        panel(T, 18, 14, 864, 424, 22),
        heading(50, 104, "Technologies & Skills", AR["skills"], 852, T, size=27, ar_size=21),
        f'<line x1="50" y1="118" x2="852" y2="118" stroke="{T["gold"]}" stroke-width="0.8" opacity=".38"/>',
    ]
    tiles = T["tiles"]
    cell = 804 / 6
    for i, (lab, mono) in enumerate(SKILLS):
        cx = 48 + cell * (i % 6 + 0.5)
        cy = 198 + (i // 6) * 126
        col = tiles[i % 4]
        col2 = tiles[(i + 2) % 4]
        spin_cls = "spin-cw a" if i % 2 == 0 else "spin-ccw a"

        # Counter-rotating outer astrolabe filigree ring
        s.append(
            f'<g class="{spin_cls}" style="animation-delay:{-i * 5.5:.1f}s">'
            f'<polygon points="{star8_pts(cx, cy, 48, 0.80)}" fill="none" stroke="{T["gold"]}" stroke-width="1.1" stroke-dasharray="4 4" opacity=".82"/>'
            f'<circle cx="{cx:.1f}" cy="{cy - 48:.1f}" r="1.9" fill="{T["gold_hi"]}"/>'
            f"</g>"
        )
        # Outer 8-point zellige ceramic star
        s.append(star8(cx, cy, 39, col, T["ink"], 1.3, ratio=0.60))
        # Inner rotated Khatam contrast star
        s.append(
            f'<g transform="rotate(22.5 {cx:.1f} {cy:.1f})">'
            f'{star8(cx, cy, 27, col2, T["gold_hi"], 0.75, op=0.88, ratio=0.68)}'
            f"</g>"
        )
        # Beveled center jewel medallion
        s.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="19" fill="{T["panel"]}" stroke="url(#gold-{T["mode"]})" stroke-width="1.6"/>')
        s.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="15.5" fill="none" stroke="{T["gold"]}" stroke-width="0.5" opacity=".45"/>')
        s.append(
            f'<text x="{cx:.1f}" y="{cy + 5}" text-anchor="middle" font-family="{SERIF}" font-size="13.8" font-weight="700" fill="{T["ink"]}">{esc(mono)}</text>'
        )
        # Label pill underneath
        s.append(
            f'<text x="{cx:.1f}" y="{cy + 64}" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="700" letter-spacing="0.3" fill="{T["ink"]}">{esc(lab)}</text>'
        )
    return svg(W, H, "".join(s), "Technologies and skills", "Twelve Alhambra zellige star medallions.", defs)


# ---------------------------------------------------------------------------
# 5. SELECTED LIVE PROJECTS TITLE BANNER (900 x 106)
# ---------------------------------------------------------------------------
def projects_title(T):
    W, H = 900, 106
    defs, bg = base(T, W, H, "p")
    s = [
        bg,
        f'<rect x="18" y="10" width="864" height="86" rx="4" fill="url(#panel-{T["mode"]})" stroke="url(#gold-{T["mode"]})" stroke-width="1.6"/>',
        f'<rect x="24" y="16" width="852" height="74" fill="none" stroke="{T["gold"]}" stroke-width="0.7" opacity=".45"/>',
        heading(48, 62, "Selected live projects", AR["projects"], 852, T, size=27, ar_size=22),
        frieze(T, 434, 686, 44, 17, 2, wave=True),
        star_twinkle(560, 26, 0.55, T, delay=-1.1),
    ]
    return svg(W, H, "".join(s), "Selected live projects", "Section heading.", defs)


# ---------------------------------------------------------------------------
# 6. LIVE PROJECT CARDS (288 x 334 — 3x2 Alhambra Mihrab Alcoves)
# ---------------------------------------------------------------------------
def card(T, idx, proj, img):
    W, H = 288, 334
    cx = W / 2
    ax, ay, aw, ah = 68, 52, 152, 126
    mode = T["mode"]
    tile = T["tiles"][(idx - 1) % 4]
    defs = (
        shared_defs(T, f"c{idx}")
        + f'<clipPath id="cp{idx}"><path d="{horseshoe(ax, ay, aw, ah)}"/></clipPath>'
        + f'<linearGradient id="seal-{idx}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{T["seal"]}"/>'
        f'<stop offset="1" stop-color="{T["seal2"]}"/>'
        f"</linearGradient>"
        + f'<radialGradient id="cvig{idx}" cx=".5" cy=".45" r=".62">'
        f'<stop offset="0.6" stop-color="#000" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#040D0C" stop-opacity="{0.38 if mode == "dark" else 0.16}"/>'
        f"</radialGradient>"
    )
    body_path = stepped_merlons(6, 6, W - 12, 7, 13) + f" V{H - 7} H6 Z"
    d1, d2 = proj["description_lines"][:2]
    tags_line = "  ·  ".join(proj.get("card_tags", proj["tags"][:3]))
    badge_txt = proj.get("badge", "LIVE")
    badge_w = max(62, len(badge_txt) * 6.2 + 18)

    g = [
        # Drop shadow & stepped-merlon card frame
        f'<path d="{body_path}" transform="translate(0,3)" fill="#000000" opacity="{T["shadow_op"]}"/>',
        f'<path d="{body_path}" fill="url(#panel-{mode})" stroke="url(#gold-{mode})" stroke-width="1.9" stroke-linejoin="round"/>',
        # Subtle tilework texture clipped softly inside card
        f'<rect x="13" y="24" width="{W - 26}" height="{H - 37}" fill="url(#c{idx}t)" opacity="{0.08 if mode == "dark" else 0.09}"/>',
        f'<rect x="13" y="24" width="{W - 26}" height="{H - 37}" fill="none" stroke="{T["gold"]}" stroke-width="0.75" opacity=".48"/>',
        # Top-left Category pill badge
        f'<rect x="20" y="29" width="{badge_w:.0f}" height="19" rx="9.5" fill="{T["panel_deep"]}" fill-opacity=".88" stroke="{tile}" stroke-width="0.9" stroke-opacity=".85"/>',
        f'<text x="{20 + badge_w / 2:.1f}" y="41.8" text-anchor="middle" font-family="{MONO}" font-size="8.4" font-weight="700" letter-spacing="0.4" fill="{T["accent"]}">{esc(badge_txt.upper())}</text>',
        # Top-right Live beacon with double ripple ring
        f'<rect x="210" y="29" width="58" height="19" rx="9.5" fill="{T["panel_deep"]}" fill-opacity=".9" stroke="{T["live"]}" stroke-width="0.9" stroke-opacity=".85"/>',
        f'<circle class="pulse-ring a" style="animation-delay:{-idx * 0.4:.1f}s" cx="222" cy="38.5" r="3" fill="none" stroke="{T["live"]}" stroke-width="1"/>',
        f'<circle class="pulse-dot a" style="animation-delay:{-idx * 0.4:.1f}s" cx="222" cy="38.5" r="2.7" fill="{T["live"]}"/>',
        f'<text x="231" y="41.8" font-family="{MONO}" font-size="8.5" font-weight="700" letter-spacing="0.8" fill="{T["ink"]}">LIVE</text>',
        # Cordoban arch surround
        f'<path d="{horseshoe(ax, ay, aw, ah, 8.5)}" fill="none" stroke="{tile}" stroke-width="6.5"/>',
        f'<path d="{horseshoe(ax, ay, aw, ah, 8.5)}" fill="none" stroke="{T["gold_hi"]}" stroke-width="6.5" stroke-dasharray="5 16" opacity=".65"/>',
        f'<path d="{horseshoe(ax, ay, aw, ah, 12.2)}" fill="none" stroke="url(#gold-{mode})" stroke-width="1.2"/>',
        f'<path d="{horseshoe(ax, ay, aw, ah, 4.5)}" fill="none" stroke="{T["gold"]}" stroke-width="0.9" opacity=".8"/>',
        # Artwork with gentle staggered breath + subtle shimmer sweep
        f'<g clip-path="url(#cp{idx})">'
        f'<image class="cbreathe a" style="animation-delay:{-idx * 3.1:.1f}s" href="{img}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" preserveAspectRatio="xMidYMid slice"/>'
        f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="url(#cvig{idx})"/>'
        f'<rect class="shimmer a" style="animation-delay:{-idx * 1.4:.1f}s;animation-duration:9s" x="{ax}" y="{ay - 20}" width="64" height="{ah + 40}" transform="skewX(-20)" fill="url(#sheen-{mode})"/>'
        f"</g>",
        f'<path d="{horseshoe(ax, ay, aw, ah)}" fill="none" stroke="{T["ink"]}" stroke-width="1.2" opacity=".85"/>',
        # Ornate Octagonal Khatam Arabic-Indic Numeral Seal
        star8(cx, 182, 20.5, f"url(#gold-{mode})", T["panel_deep"], 0.9, ratio=0.68),
        star8(cx, 182, 17, f"url(#seal-{idx})", T["gold_hi"], 0.8, ratio=0.72),
        ar_calligraphy(
            AR_NUMS[idx - 1],
            cx,
            182,
            size=15.8,
            fill="#FFF7E2",
            font="Aref Ruqaa Bold",
            anchor="middle",
            valign="middle",
        ),
        # Title & Description
        f'<text x="{cx:.0f}" y="220" text-anchor="middle" font-family="{SERIF}" font-size="18.5" font-weight="700" letter-spacing="0.3" fill="{T["ink"]}">{esc(proj["title"])}</text>',
        f'<text x="{cx:.0f}" y="240" text-anchor="middle" font-family="{SANS}" font-size="11.4" fill="{T["soft"]}">{esc(d1)}</text>',
        f'<text x="{cx:.0f}" y="256" text-anchor="middle" font-family="{SANS}" font-size="11.4" fill="{T["soft"]}">{esc(d2)}</text>',
        # Tech tags
        f'<text x="{cx:.0f}" y="279" text-anchor="middle" font-family="{MONO}" font-size="9.8" font-weight="700" fill="{T["accent"]}">{esc(tags_line)}</text>',
        # Live domain footer pill
        f'<line x1="26" y1="291" x2="{W - 26}" y2="291" stroke="{T["gold"]}" stroke-opacity=".35"/>',
        f'<rect x="24" y="299" width="{W - 48}" height="22" rx="11" fill="{T["panel_deep"]}" fill-opacity=".68" stroke="{T["gold"]}" stroke-width="0.7" stroke-opacity=".4"/>',
        f'<text x="{cx:.0f}" y="313.5" text-anchor="middle" font-family="{MONO}" font-size="9.4" fill="{T["ink"]}">{esc(proj["display_url"])}  ↗</text>',
    ]
    return svg(W, H, "".join(g), f'Project {proj["title"]}', f'{proj["title"]}: {proj["description"]}', defs, animated=True)


# ---------------------------------------------------------------------------
# 7. FOOTER (900 x 380 — Shaded Muqarnas Vault, Swaying Lanterns & Calligraphy)
# ---------------------------------------------------------------------------
def footer(T):
    W, H = 900, 380
    defs, bg = base(T, W, H, "f")
    mode = T["mode"]
    defs += (
        f'<radialGradient id="fcglow" cx=".5" cy=".5" r=".5">'
        f'<stop offset="0" stop-color="{T["warm"]}" stop-opacity="{0.22 if mode == "dark" else 0.14}"/>'
        f'<stop offset="1" stop-color="{T["warm"]}" stop-opacity="0"/>'
        f"</radialGradient>"
    )

    s = [
        bg,
        # Sculpted 3-tier shaded Alhambra Muqarnas vault across top
        muqarnas_vault(T, -20, W + 20, 0, 3),
        # Soft warm courtyard glow behind Arabic calligraphic centerpiece
        f'<ellipse cx="450" cy="176" rx="280" ry="74" fill="url(#fcglow)"/>',
        # Symmetrical hanging swaying brass lanterns
        fanous_lantern(T, 114, 72, scale=0.96, delay=-0.6),
        fanous_lantern(T, 786, 72, scale=0.96, delay=-3.8),
        # Floating starlight motes
        floating_mote(220, 210, 1.8, T, delay=-1.2, dur=8.2),
        floating_mote(275, 160, 1.4, T, delay=-4.5, dur=9.4),
        floating_mote(630, 165, 1.5, T, delay=-2.4, dur=8.6),
        floating_mote(682, 215, 1.9, T, delay=-5.1, dur=7.8),
        star_twinkle(450, 106, 0.88, T, delay=-0.4),
        star_twinkle(210, 132, 0.48, T, delay=-2.2),
        star_twinkle(690, 132, 0.48, T, delay=-3.4),
    ]

    # Hero Arabic Calligraphic Centerpiece: ابنِ ✦ اكتشف ✦ افهم on a shared calligraphic baseline
    w_right, w_mid, w_left = AR["footer_words"]
    sz = 31
    wr = ar_width(w_right, size=sz, font="Aref Ruqaa Bold")
    wm = ar_width(w_mid, size=sz, font="Aref Ruqaa Bold")
    wl = ar_width(w_left, size=sz, font="Aref Ruqaa Bold")
    gap = 42
    total_w = wr + wm + wl + gap * 2
    x_right_edge = 450 + total_w / 2
    y_ar_base = 172
    y_orn = 160

    # Right word (ابنِ)
    s.append(
        ar_calligraphy(
            w_right,
            x_right_edge,
            y_ar_base,
            size=sz,
            fill=f"url(#callig-{mode})",
            font="Aref Ruqaa Bold",
            anchor="end",
            valign="baseline",
            cls="cglow a",
        )
    )
    # Star divider 1
    star1_x = x_right_edge - wr - gap / 2
    s.append(khatam_rosette(star1_x, y_orn, 7.5, T["tiles"][1], T["tiles"][0], T["gold_hi"], T["ink"]))
    # Middle word (اكتشف)
    x_mid_right = x_right_edge - wr - gap
    s.append(
        ar_calligraphy(
            w_mid,
            x_mid_right,
            y_ar_base,
            size=sz,
            fill=f"url(#callig-{mode})",
            font="Aref Ruqaa Bold",
            anchor="end",
            valign="baseline",
            cls="cglow a",
        )
    )
    # Star divider 2
    star2_x = x_mid_right - wm - gap / 2
    s.append(khatam_rosette(star2_x, y_orn, 7.5, T["tiles"][0], T["tiles"][3], T["gold_hi"], T["ink"]))
    # Left word (افهم)
    x_left_right = x_mid_right - wm - gap
    s.append(
        ar_calligraphy(
            w_left,
            x_left_right,
            y_ar_base,
            size=sz,
            fill=f"url(#callig-{mode})",
            font="Aref Ruqaa Bold",
            anchor="end",
            valign="baseline",
            cls="cglow a",
        )
    )

    # Symmetrical Arabesque Brackets framing the Arabic centerpiece
    s.append(arabesque_bracket(T, 450 - total_w / 2 - 72, y_orn, direction=1, size=0.95))
    s.append(arabesque_bracket(T, 450 + total_w / 2 + 72, y_orn, direction=-1, size=0.95))

    # English motto & subtitle
    s.append(
        f'<text x="450" y="216" text-anchor="middle" font-family="{SERIF}" font-size="27" letter-spacing="1.2" fill="{T["ink"]}">{esc(FOOTER_1)}</text>'
    )
    s.append(
        f'<text x="450" y="246" text-anchor="middle" font-family="{SANS}" font-size="12.5" letter-spacing="1.4" fill="{T["soft"]}">{esc(FOOTER_2)}</text>'
    )

    # Animated Alhambra Zellige Frieze
    s.append(frieze(T, 16, W - 16, H - 90, 24, 0, wave=True))

    # Regal Bottom Colophon Bar with Vectorized Arabic Brand Signature
    s.append(f'<rect x="0" y="{H - 40}" width="{W}" height="40" fill="{T["band"]}"/>')
    s.append(f'<line x1="0" y1="{H - 40}" x2="{W}" y2="{H - 40}" stroke="url(#gold-{mode})" stroke-width="2.2"/>')
    s.append(
        f'<text x="30" y="{H - 16}" font-family="{SANS}" font-size="10.8" fill="#E8DEC6" opacity=".88">{esc(ART_CREDIT)}</text>'
    )
    # Right side: NashirTech · ناشر تك
    brand_w = ar_width(AR["brand"], size=14.5, font="Aref Ruqaa Bold")
    s.append(
        ar_calligraphy(
            AR["brand"],
            870,
            H - 20,
            size=14.5,
            fill="#F0BE7E",
            font="Aref Ruqaa Bold",
            anchor="end",
            valign="middle",
        )
    )
    s.append(
        f'<text x="{870 - brand_w - 10:.1f}" y="{H - 16}" text-anchor="end" font-family="{SANS}" font-size="11.5" font-weight="700" letter-spacing="0.4" fill="#F0BE7E">NashirTech  ·</text>'
    )

    return svg(W, H, "".join(s), "Footer", f"{FOOTER_1}. {FOOTER_2}.", defs)


def pic(name, alt, href=None, width="100%"):
    p = (
        f'<picture>\n<source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
        f'<source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
        f'<img alt="{html.escape(alt)}" src="assets/{name}-light.svg" width="{width}">\n</picture>'
    )
    return f'<a href="{href}">\n{p}\n</a>' if href else p


def main():
    for old in ASSETS.glob("card-*.svg"):
        old.unlink()

    thumbs = [b64_crop(box, (260, 260)) for box in PROJECT_CROPS]
    imgs = {"hero": b64_crop(HERO_CROP, (640, 854), 84), 1: thumbs[0]}

    for th, T in THEMES.items():
        save("hero", th, hero(T, imgs))
        save("btn-github", th, button(T, "GitHub", delay=0.0))
        save("btn-linkedin", th, button(T, "LinkedIn", delay=-1.8))
        save("btn-portfolio", th, button(T, "Portfolio", delay=-3.6))
        save("about", th, about(T))
        save("skills", th, skills(T))
        save("projects-title", th, projects_title(T))
        save("footer", th, footer(T))
        for i, proj in enumerate(PROJECTS):
            save(f'card-{proj["id"]}', th, card(T, i + 1, proj, thumbs[i % len(thumbs)]))

    cards = [pic(f'card-{p["id"]}', f'{p["title"]}: {p["description"]}', p["live_url"], "32%") for p in PROJECTS]
    md = [
        '<div align="center">',
        "",
        pic("hero", f"{FULL_NAME}, {ROLE.title()}. Andalusian horseshoe arch with Cordoban voussoirs and Arabic calligraphy."),
        "",
        pic("btn-github", "GitHub profile", GITHUB, "160")
        + "&nbsp;"
        + pic("btn-linkedin", "LinkedIn profile", LINKEDIN, "160")
        + "&nbsp;"
        + pic("btn-portfolio", "Portfolio website", PORTFOLIO, "160"),
        "",
        pic("about", "About me and my journey from languages to areas"),
        "",
        pic("skills", "Technologies and skills"),
        "",
        pic("projects-title", "Selected live projects"),
        "",
        "\n".join(cards[:3]),
        "",
        "\n".join(cards[3:6]),
        "",
        pic("footer", FOOTER_1 + ". " + FOOTER_2),
        "",
        f'<sub><a href="{PORTFOLIO}">{PORTFOLIO_DISPLAY}</a> &nbsp;·&nbsp; <a href="{LINKEDIN}">LinkedIn</a> &nbsp;·&nbsp; <a href="{GITHUB}">GitHub</a></sub>',
        "",
        "</div>",
        "",
    ]
    (ROOT / "README.md").write_text("\n".join(md), encoding="utf-8")
    shaper_mode = "HarfBuzz/PangoCairo vectorized calligraphy" if SHAPER.available else "fallback text"
    print(f"[Andalusian Heritage — Alhambra Edition] Generated 3x2 assets & README.md ({shaper_mode})")


if __name__ == "__main__":
    main()
