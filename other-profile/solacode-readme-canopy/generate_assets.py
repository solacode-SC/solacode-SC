#!/usr/bin/env python3
"""
Profile README generator: "Canopy Spiral" — Enhanced 3x2 Live Botanical Edition.
Reads central data from ../../profile-data.json.
"""
import base64
import html
import io
import json
import math
import os
import random
import re
import textwrap
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
DATA = json.loads((REPO_ROOT / "profile-data.json").read_text(encoding="utf-8"))

NAME_1, NAME_2 = DATA["profile"]["first_name"], DATA["profile"]["last_name"]
FULL_NAME = DATA["profile"]["name"]
HANDLE = DATA["profile"]["handle"]
GITHUB = DATA["links"]["github"]
PORTFOLIO = DATA["links"]["portfolio"]
PORTFOLIO_DISPLAY = DATA["links"]["portfolio_display"]
LINKEDIN = DATA["links"]["linkedin"]
ROLE = "Software Engineer"
PILLARS = DATA["pillars"]
TAGLINE = DATA["profile"]["tagline_lines"]
ABOUT = " ".join(DATA["profile"]["about"])
FACTS = DATA["profile"]["facts"]
FOCUS = "Focus: " + DATA["profile"]["focus"]
JOURNEY = [
    ("C / C++", "Systems"),
    ("Python", "Backend & AI"),
    ("TypeScript", "Web & Tools"),
    ("Docker", "Infrastructure"),
    ("Linux", "DevOps"),
]
SKILLS = [(s["name"], s["short"]) for s in DATA["skills"]]
PROJECTS = DATA["projects"]

# 6 square crop boxes in art/source.jpg (736x1308)
PROJECT_CROPS = [
    (496, 260, 736, 500),
    (340, 150, 580, 390),
    (0, 430, 240, 670),
    (400, 880, 640, 1120),
    (60, 950, 300, 1190),
    (420, 560, 660, 800),
]

FOOTER_1 = "Build  ·  Explore  ·  Understand"
FOOTER_2 = "Software Engineering · Systems · AI · Mathematics"
ART_CREDIT = "Canopy Spiral Botanical Edition"
SIGNATURE = "NashirTech \u00b7 \u0646\u0627\u0634\u0631 \u062a\u0643"
SOURCE = ROOT / "art" / "source.jpg"
HERO_CROP = (0, 120, 736, 1174)

SERIF = "Georgia,'Iowan Old Style','Palatino Linotype','DejaVu Serif',serif"
SANS = "'Trebuchet MS','Segoe UI',Verdana,'DejaVu Sans',sans-serif"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Consolas,Menlo,monospace"

THEMES = {
    "dark": dict(
        bg="#0C1810",
        bg2="#18351F",
        panel="#152C1D",
        panel2="#1C3926",
        ink="#EAF1D2",
        soft="#B9CBA6",
        accent="#C9E66B",
        live="#69F0AE",
        line="#8DB33A",
        twig="#6F9A78",
        twigop=".55",
        disc="#EAF1D2",
        disctxt="#12261A",
        btn="#B7D957",
        btntxt="#10200F",
        band="#08110B",
        dots=["#8DB33A", "#A9D04B", "#5E9B6B", "#C9E66B", "#6FA89A"],
        blob_op=".55",
    ),
    "light": dict(
        bg="#F4F6E0",
        bg2="#DCE8BE",
        panel="#FBFCEB",
        panel2="#EFF4D9",
        ink="#1B2D19",
        soft="#455E3D",
        accent="#3C6A1B",
        live="#1A8249",
        line="#6E9A2C",
        twig="#3B2D20",
        twigop=".45",
        disc="#FBFCEB",
        disctxt="#1B2D19",
        btn="#3C6A1B",
        btntxt="#F6F8E6",
        band="#1B2D19",
        dots=["#6E9A2C", "#8DB33A", "#4E8A5E", "#A9C84A", "#5E9AA0"],
        blob_op=".7",
    ),
}

CSS = """
.a{animation-timing-function:ease-in-out;animation-iteration-count:infinite;animation-direction:alternate}
.kb{transform-box:fill-box;transform-origin:50% 40%;animation-name:kb;animation-duration:40s}
.spin{transform-box:fill-box;transform-origin:center;animation-name:spin;animation-duration:160s;animation-timing-function:linear;animation-direction:normal}
.sway{transform-box:fill-box;transform-origin:center;animation-name:sway;animation-duration:18s}
.bob{animation-name:bob;animation-duration:9s}
.flow{animation-name:flow;animation-duration:9s;animation-timing-function:linear;animation-direction:normal}
.pulse{animation-name:pulse;animation-duration:2.4s}
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.05)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes sway{from{transform:rotate(-3deg)}to{transform:rotate(3deg)}}
@keyframes bob{from{transform:translateY(0)}to{transform:translateY(-8px)}}
@keyframes flow{to{stroke-dashoffset:-64}}
@keyframes pulse{from{opacity:1}to{opacity:.3}}
@media (prefers-reduced-motion: reduce){.a{animation:none}}
"""


def esc(s):
    return html.escape(str(s), quote=False)


def b64_crop(box, size, q=82):
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


def wave(x0, x1, y, amp, wl, ph=0.0, step=6):
    pts, x = [], x0
    while x <= x1:
        pts.append(f"{x:.1f},{y + amp * math.sin((x - x0) / wl * 2 * math.pi + ph):.1f}")
        x += step
    return "M" + " L".join(pts)


def blob_path(cx, cy, rx, ry, seed, n=9, jit=0.1):
    r = random.Random(seed)
    pts = []
    for i in range(n):
        a = i * 2 * math.pi / n
        k = 1 + r.uniform(-jit, jit)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + " Z"


def spiral_d(R, turns, step=0.25):
    pts, th, tmax = [], 0.0, turns * 2 * math.pi
    while th <= tmax:
        r = R * th / tmax
        pts.append(f"{r * math.cos(th):.1f},{r * math.sin(th):.1f}")
        th += step
    return "M" + " L".join(pts)


def spiral(cx, cy, R, turns, color, w=2, op=1.0, rot=0, spin=False, delay=0):
    guard = f'<circle r="{R}" fill="none" stroke="none"/>'
    path = f'<path d="{spiral_d(R, turns)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>'
    inner = guard + path
    if spin:
        inner = f'<g class="spin a" style="animation-delay:-{delay}s">{inner}</g>'
    return f'<g transform="translate({cx},{cy}) rotate({rot})">{inner}</g>'


def phyllotaxis(cx, cy, n, spread, T, spin_delay=None):
    out = [f'<circle r="{spread * math.sqrt(n) + 4:.0f}" fill="none" stroke="none"/>']
    for i in range(1, n + 1):
        th = i * 2.399963
        rr = spread * math.sqrt(i)
        out.append(f'<circle cx="{rr * math.cos(th):.1f}" cy="{rr * math.sin(th):.1f}" r="{1.2 + 2.0 * i / n:.1f}" fill="{T["dots"][i % 5]}"/>')
    g = "".join(out)
    if spin_delay is not None:
        g = f'<g class="spin a" style="animation-delay:-{spin_delay}s;animation-duration:90s">{g}</g>'
    return f'<g transform="translate({cx:.1f},{cy:.1f})">{g}</g>'


def twig(T, x, y, ang, L, seed, depth=5, w=3.2):
    r = random.Random(seed)
    segs = []

    def grow(x, y, a, L, d, w):
        a2 = a + r.uniform(-0.35, 0.35)
        x2, y2 = x + L * math.cos(a2), y + L * math.sin(a2)
        mx, my = (x + x2) / 2 + r.uniform(-L, L) * 0.15, (y + y2) / 2 + r.uniform(-L, L) * 0.15
        segs.append(f'<path d="M{x:.0f},{y:.0f} Q{mx:.0f},{my:.0f} {x2:.0f},{y2:.0f}" stroke-width="{max(w, 0.8):.1f}"/>')
        if d > 0:
            grow(x2, y2, a2 + r.uniform(0.25, 0.6), L * 0.76, d - 1, w * 0.66)
            if r.random() < 0.8:
                grow(x2, y2, a2 - r.uniform(0.3, 0.7), L * 0.7, d - 1, w * 0.6)

    grow(x, y, ang, L, depth, w)
    return f'<g fill="none" stroke="{T["twig"]}" stroke-linecap="round" opacity="{T["twigop"]}">{"".join(segs)}</g>'


def base(T, W, H, sid="s"):
    defs = (
        f'<linearGradient id="{sid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["bg"]}"/>'
        f'<stop offset="1" stop-color="{T["bg2"]}"/></linearGradient>'
    )
    return defs, f'<rect width="{W}" height="{H}" fill="url(#{sid}g)"/>'


def heading(x, y, text, T, size=28):
    return (
        spiral(x + 12, y - 9, 11, 2.2, T["accent"], 2.2)
        + f'<text x="{x + 34}" y="{y}" font-family="{SERIF}" font-size="{size}" font-style="italic" letter-spacing=".8" fill="{T["ink"]}">{esc(text)}</text>'
    )


def scatter_spirals(T, W, H, seed, n, rmin, rmax, op=(0.15, 0.35), avoid=None, spin_n=3):
    r = random.Random(seed)
    out = []
    for i in range(n):
        for _ in range(20):
            x, y, R = r.uniform(0, W), r.uniform(0, H), r.uniform(rmin, rmax)
            if not avoid or not (avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]):
                break
        out.append(
            spiral(
                round(x),
                round(y),
                round(R),
                r.choice((2.5, 3, 3.5)),
                T["line"],
                r.choice((1.4, 2, 2.6)),
                round(r.uniform(*op), 2),
                r.randint(0, 359),
                spin=(i < spin_n),
                delay=r.randint(0, 80),
            )
        )
    return "".join(out)


def hero(T, imgs):
    W, H = 900, 580
    defs, bg = base(T, W, H, "h")
    bx, by, brx, bry = 670, 292, 182, 262
    blob = blob_path(bx, by, brx, bry, 12, 9, 0.07)
    defs += f'<clipPath id="hclip"><path d="{blob}"/></clipPath><clipPath id="hav"><circle cx="64" cy="34" r="14"/></clipPath>'
    defs += '<clipPath id="hf1"><circle cx="455" cy="500" r="32"/></clipPath><clipPath id="hf2"><circle cx="868" cy="62" r="26"/></clipPath>'
    s = [bg, scatter_spirals(T, 500, H, 3, 7, 40, 120, (0.1, 0.22), avoid=(40, 90, 480, 470), spin_n=2)]
    s.append(twig(T, 0, 590, -1.2, 78, 5, 5, 4.2))
    s.append(twig(T, 520, -10, 1.5, 60, 8, 4, 3))
    s.append(f'<image href="{imgs[0]}" x="50" y="20" width="28" height="28" clip-path="url(#hav)" preserveAspectRatio="xMidYMid slice"/>')
    s.append(f'<circle cx="64" cy="34" r="14" fill="none" stroke="{T["accent"]}" stroke-width="1.6"/>')
    s.append(f'<text x="86" y="39" font-family="{MONO}" font-size="12.5" fill="{T["soft"]}">{esc(HANDLE)} / README</text>')
    s.append(f'<path d="{wave(50, 400, 64, 3, 70)}" fill="none" stroke="{T["line"]}" stroke-width="1.4" opacity=".8"/>')
    s.append(f'<text x="52" y="132" font-family="{SERIF}" font-size="20" font-style="italic" fill="{T["soft"]}">hi, i\'m</text>')
    s.append(spiral(122, 126, 9, 2, T["accent"], 2))
    s.append(f'<text x="50" y="202" font-family="{SERIF}" font-size="60" font-style="italic" fill="{T["ink"]}">{esc(NAME_1)}</text>')
    s.append(f'<text x="96" y="268" font-family="{SERIF}" font-size="60" font-style="italic" fill="{T["ink"]}">{esc(NAME_2)}</text>')
    s.append(f'<text x="98" y="322" font-family="{SANS}" font-size="14" font-weight="700" letter-spacing="4" fill="{T["accent"]}">{esc(ROLE)}</text>')
    sep = "\u00a0\u00a0|\u00a0\u00a0"
    s.append(f'<text x="98" y="354" font-family="{SERIF}" font-size="17.5" font-style="italic" fill="{T["ink"]}">{esc(sep.join(PILLARS))}</text>')
    for i, line in enumerate(TAGLINE):
        s.append(f'<text x="{60 + i * 10}" y="{408 + i * 23}" font-family="{SERIF}" font-size="15.5" fill="{T["soft"]}">{esc(line)}</text>')
    s.append(f'<path class="sway a" d="{blob_path(bx, by, brx + 14, bry + 14, 12, 9, 0.07)}" fill="none" stroke="{T["accent"]}" stroke-width="1.2" opacity=".7"/>')
    s.append(f'<path class="sway a" style="animation-direction:alternate-reverse;animation-duration:24s" d="{blob_path(bx, by, brx + 28, bry + 26, 12, 9, 0.07)}" fill="none" stroke="{T["line"]}" stroke-width=".9" opacity=".5"/>')
    s.append(f'<g clip-path="url(#hclip)"><image class="kb a" href="{imgs["hero"]}" x="{bx - 185}" y="{by - 267}" width="370" height="534" preserveAspectRatio="xMidYMid slice"/></g>')
    s.append(
        f'<g class="bob a"><g clip-path="url(#hf1)"><image href="{imgs[2]}" x="423" y="468" width="64" height="64"/></g>'
        f'<circle cx="455" cy="500" r="32" fill="none" stroke="{T["accent"]}" stroke-width="1.4"/></g>'
    )
    s.append(
        f'<g class="bob a" style="animation-delay:-4s"><g clip-path="url(#hf2)"><image href="{imgs[4]}" x="842" y="36" width="52" height="52"/></g>'
        f'<circle cx="868" cy="62" r="26" fill="none" stroke="{T["accent"]}" stroke-width="1.4"/></g>'
    )
    return svg(W, H, "".join(s), f"{FULL_NAME}: {ROLE}", "Canopy Spiral profile header.", defs)


def button(T, label):
    body = (
        f'<path d="M5,20 C30,2 120,2 145,20 C120,38 30,38 5,20 Z" fill="{T["btn"]}"/>'
        + spiral(32, 20, 7, 2, T["btntxt"], 1.8)
        + f'<text x="88" y="25" text-anchor="middle" font-family="{SERIF}" font-size="15" font-style="italic" letter-spacing=".6" fill="{T["btntxt"]}">{esc(label)}</text>'
    )
    return svg(150, 40, body, label, f"Button linking to {label}", animated=False)


def about(T):
    W, H = 900, 392
    defs, bg = base(T, W, H, "a")
    s = [bg, f'<path d="{blob_path(450, 196, 430, 172, 4, 10, 0.06)}" fill="{T["panel"]}" opacity="{T["blob_op"]}"/>']
    s.append(spiral(770, 210, 150, 3.5, T["line"], 2, 0.22, 0, spin=True))
    s.append(twig(T, 900, 400, -2.6, 70, 11, 4, 3))
    s.append(heading(60, 78, "about", T))
    s.append(heading(520, 78, "my journey", T))
    lines = textwrap.wrap(ABOUT, 50)
    g = []
    for i, line in enumerate(lines):
        g.append(f'<text x="60" y="{122 + i * 24}" font-family="{SERIF}" font-size="14.5" fill="{T["ink"]}">{esc(line)}</text>')
    y = 122 + 24 * len(lines) + 24
    for line in textwrap.wrap(FACTS, 58):
        g.append(f'<text x="60" y="{y}" font-family="{SANS}" font-size="12" fill="{T["soft"]}">{esc(line)}</text>')
        y += 18
    g.append(f'<text x="60" y="{y + 8}" font-family="{SANS}" font-size="12.5" font-weight="700" fill="{T["accent"]}">{esc(FOCUS)}</text>')
    s.append(f'<g transform="rotate(-.8 60 122)">{"".join(g)}</g>')
    for i, (lang, area) in enumerate(JOURNEY):
        yy = 134 + i * 44
        lx = 520 + round(9 * math.sin(i * 1.4))
        x1 = lx + len(lang) * 10.4 + 14
        x2 = 850 - len(area) * 7.6 - 30
        s.append(f'<text x="{lx}" y="{yy}" font-family="{SERIF}" font-size="18" font-style="italic" fill="{T["ink"]}">{esc(lang)}</text>')
        s.append(f'<path class="flow a" d="{wave(round(x1), round(x2), yy - 5, 3, 50, i)}" fill="none" stroke="{T["line"]}" stroke-width="3" stroke-linecap="round" stroke-dasharray="0 8"/>')
        s.append(f'<text x="850" y="{yy}" text-anchor="end" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{T["accent"]}">{esc(area)}</text>')
    return svg(W, H, "".join(s), "About and journey", "About and journey.", defs)


def skills(T):
    W, H = 900, 360
    defs, bg = base(T, W, H, "k")
    s = [
        bg,
        f'<path d="{blob_path(450, 190, 430, 160, 9, 10, 0.06)}" fill="{T["panel"]}" opacity="{T["blob_op"]}"/>',
        scatter_spirals(T, W, H, 6, 5, 50, 110, (0.08, 0.16), spin_n=1),
        heading(60, 78, "technologies & skills", T),
    ]
    cell = 800 / 6
    for i, (lab, mono) in enumerate(SKILLS):
        row, col = divmod(i, 6)
        cx = 50 + cell * (col + 0.5) + row * 22
        cy = 160 + row * 116 + round(9 * math.sin(col * 1.7 + row))
        s.append(phyllotaxis(cx, cy, 60, 4.6, T, spin_delay=i * 11))
        s.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="17" fill="{T["disc"]}"/>')
        s.append(f'<text x="{cx:.1f}" y="{cy + 4.5}" text-anchor="middle" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{T["disctxt"]}">{esc(mono)}</text>')
        s.append(f'<text x="{cx:.1f}" y="{cy + 58}" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="700" fill="{T["ink"]}">{esc(lab)}</text>')
    return svg(W, H, "".join(s), "Technologies and skills", "Twelve seed-like spirals.", defs)


def projects_title(T):
    W, H = 900, 92
    defs, bg = base(T, W, H, "p")
    s = [
        bg,
        heading(60, 56, "selected live projects", T, 28),
        f'<path d="{wave(385, 690, 48, 7, 110)}" fill="none" stroke="{T["line"]}" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="0 8" class="flow a"/>',
        f'<rect x="708" y="34" width="138" height="27" rx="13.5" fill="{T["panel"]}" stroke="{T["accent"]}" stroke-opacity=".75"/>',
        f'<circle class="pulse a" cx="725" cy="47.5" r="3.4" fill="{T["live"]}"/>',
        f'<text x="736" y="51.3" font-family="{MONO}" font-size="10" font-weight="700" letter-spacing="1" fill="{T["ink"]}">6 DEPLOYED APPS</text>',
    ]
    return svg(W, H, "".join(s), "Selected live projects", "Section heading.", defs)


def card(T, idx, proj, img):
    W, H = 288, 286
    cx, cy, r = 144, 86, 56
    defs = (
        f'<linearGradient id="cb{idx}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["panel"]}"/>'
        f'<stop offset="1" stop-color="{T["panel2"]}"/></linearGradient>'
        f'<clipPath id="c{idx}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
    )
    d1, d2 = proj["description_lines"][:2]
    tags_line = " \u00b7 ".join(proj.get("card_tags", proj["tags"][:3]))
    g = [
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="url(#cb{idx})" stroke="{T["line"]}" stroke-opacity=".48" stroke-width="1.3"/>',
        # Top-left index & top-right LIVE badge
        f'<text x="18" y="29" font-family="{SERIF}" font-size="16" font-style="italic" font-weight="700" fill="{T["accent"]}">{esc(proj["number"])}</text>',
        f'<rect x="214" y="14" width="58" height="20" rx="10" fill="{T["bg"]}" fill-opacity=".85" stroke="{T["live"]}" stroke-opacity=".75"/>',
        f'<circle class="pulse a" cx="226" cy="24" r="3" fill="{T["live"]}"/>',
        f'<text x="235" y="27.5" font-family="{MONO}" font-size="8.8" font-weight="700" letter-spacing=".8" fill="{T["ink"]}">LIVE</text>',
        # Spiral halo & canopy medallion
        spiral(cx, cy, 80, 3, T["line"], 1.5, 0.34, idx * 45),
        f'<g clip-path="url(#c{idx})"><image href="{img}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" preserveAspectRatio="xMidYMid slice"/></g>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{T["accent"]}" stroke-width="2.2"/>',
        f'<circle cx="{cx + 5}" cy="{cy - 3}" r="{r + 8}" fill="none" stroke="{T["line"]}" stroke-width="1" opacity=".68"/>',
        # Title & description
        f'<text x="{cx}" y="176" text-anchor="middle" font-family="{SERIF}" font-size="18.5" font-style="italic" font-weight="700" fill="{T["ink"]}">{esc(proj["title"])}</text>',
        f'<text x="{cx}" y="198" text-anchor="middle" font-family="{SANS}" font-size="11.5" fill="{T["soft"]}">{esc(d1)}</text>',
        f'<text x="{cx}" y="214" text-anchor="middle" font-family="{SANS}" font-size="11.5" fill="{T["soft"]}">{esc(d2)}</text>',
        # Tags
        f'<text x="{cx}" y="238" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="{T["accent"]}">{esc(tags_line)}</text>',
        # Live domain footer
        f'<line x1="24" y1="252" x2="{W - 24}" y2="252" stroke="{T["line"]}" stroke-opacity=".35"/>',
        f'<text x="{cx}" y="270" text-anchor="middle" font-family="{MONO}" font-size="9.5" fill="{T["soft"]}">{esc(proj["display_url"])}  ↗</text>',
    ]
    return svg(W, H, "".join(g), f'Project {proj["title"]}', f'{proj["title"]}: {proj["description"]}', defs, animated=True)


def footer(T):
    W, H = 900, 310
    defs, bg = base(T, W, H, "f")
    s = [bg, scatter_spirals(T, W, H - 40, 17, 26, 16, 52, (0.25, 0.55), spin_n=4)]
    s.append(twig(T, 0, H - 34, -1.0, 90, 3, 5, 4.6))
    s.append(twig(T, W, H - 34, -2.1, 86, 6, 5, 4.4))
    s.append(f'<path d="{blob_path(450, 92, 330, 62, 2, 9, 0.05)}" fill="{T["bg"]}" opacity=".88"/>')
    s.append(f'<text x="450" y="94" text-anchor="middle" font-family="{SERIF}" font-size="31" font-style="italic" letter-spacing="1" fill="{T["ink"]}">{esc(FOOTER_1)}</text>')
    s.append(f'<text x="450" y="124" text-anchor="middle" font-family="{SANS}" font-size="13" letter-spacing="1" fill="{T["soft"]}">{esc(FOOTER_2)}</text>')
    s.append(f'<rect x="0" y="{H - 34}" width="{W}" height="34" fill="{T["band"]}"/>')
    s.append(f'<text x="50" y="{H - 13}" font-family="{SANS}" font-size="11" fill="#EAF1D2">{esc(ART_CREDIT)}</text>')
    s.append(f'<text x="850" y="{H - 13}" text-anchor="end" font-family="{SANS}" font-size="11.5" font-weight="700" fill="#C9E66B">{esc(SIGNATURE)}</text>')
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

    thumbs = [b64_crop(box, (220, 220)) for box in PROJECT_CROPS]
    imgs = {"hero": b64_crop(HERO_CROP, (556, 794), 80), 0: thumbs[0], 2: thumbs[2], 4: thumbs[4]}
    for th, T in THEMES.items():
        save("hero", th, hero(T, imgs))
        save("btn-github", th, button(T, "GitHub"))
        save("btn-linkedin", th, button(T, "LinkedIn"))
        save("btn-portfolio", th, button(T, "Portfolio"))
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
        pic("hero", f"{FULL_NAME}, {ROLE}. A tree canopy whose leaves swirl into spirals."),
        "",
        pic("btn-github", "GitHub profile", GITHUB, "150")
        + "&nbsp;"
        + pic("btn-linkedin", "LinkedIn profile", LINKEDIN, "150")
        + "&nbsp;"
        + pic("btn-portfolio", "Portfolio website", PORTFOLIO, "150"),
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
    print("[Canopy Spiral] Generated 3x2 live portfolio assets & README.md")


if __name__ == "__main__":
    main()
