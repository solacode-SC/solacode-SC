#!/usr/bin/env python3
"""Swirl / flow-field edition — Enhanced 3x2 Live Portfolio Edition.
Pure Python, zero external dependencies. Reads ../../profile-data.json.
Art system:
  - sky      -> evenly-spaced streamlines of a multi-vortex field
  - roses    -> archimedean spirals
  - fields   -> layered sine contour bands
  - cards    -> 6 bespoke algorithmic motifs for the 6 live deployed projects
"""
import html
import json
import math
import os
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "assets"
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / "profile-data.json").read_text(encoding="utf-8"))

MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Consolas,Menlo,monospace"
SERIF = "Georgia,'Iowan Old Style','Palatino Linotype','DejaVu Serif',serif"
JP = "'Noto Sans JP','Yu Gothic','Hiragino Sans',sans-serif"

THEMES = {
    "dark": dict(
        bg1="#041114",
        bg2="#0a2126",
        fg="#ecf4ef",
        mute="#8db2ac",
        acc="#f0d672",
        acc2="#7fc9bf",
        live="#5de6a4",
        line="#1d4a50",
        card="#08191d",
        card2="#0c2429",
        pill="#051316",
        pal=["#2f8f98", "#4fb09b", "#8fc99c", "#5aaebb"],
        warm="#f0d672",
        roof="#dc7a52",
    ),
    "light": dict(
        bg1="#fbf7ea",
        bg2="#efe8d2",
        fg="#12343a",
        mute="#537376",
        acc="#96640a",
        acc2="#1d6670",
        live="#168052",
        line="#c3d2c6",
        card="#fffdf4",
        card2="#f6f0de",
        pill="#f0ebd8",
        pal=["#1d6670", "#2f8a7e", "#5f9a74", "#3f8e9c"],
        warm="#c9971c",
        roof="#b6532f",
    ),
}

NAME = DATA["profile"]["name"]
GITHUB = DATA["links"]["github"]
LINKEDIN = DATA["links"]["linkedin"]
PORTFOLIO = DATA["links"]["portfolio"]
PORTFOLIO_DISPLAY = DATA["links"]["portfolio_display"]

JOURNEY = [
    ("C / C++", "Systems"),
    ("Python", "Backend & AI"),
    ("TypeScript", "Web & Tools"),
    ("Docker", "Infrastructure"),
    ("Linux", "DevOps"),
]
SKILLS = [(s["name"], s["short"]) for s in DATA["skills"]]
PROJECTS = DATA["projects"]

STYLE = """<style>
.spin{transform-box:fill-box;transform-origin:center;animation:spin 70s linear infinite}
.spin.r{animation-direction:reverse;animation-duration:95s}
@keyframes spin{to{transform:rotate(360deg)}}
.dots{stroke-dasharray:.1 34;stroke-linecap:round;animation:run 18s linear infinite}
@keyframes run{to{stroke-dashoffset:-341}}
.pulse{animation:pulse 2.6s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
@media (prefers-reduced-motion:reduce){.spin,.dots,.pulse{animation:none}}
</style>"""


def esc(s):
    return html.escape(str(s), quote=False)


def f1(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pts_path(pts):
    return "M" + "L".join(f"{f1(x)} {f1(y)}" for x, y in pts)


VORT = [
    (700, 170, 1.0, 0.20, 44),
    (570, 285, -0.6, 0.12, 24),
    (850, 62, -0.55, 0.14, 22),
    (545, 60, 0.5, 0.12, 24),
    (860, 290, 0.55, 0.12, 22),
]


def vel(x, y):
    vx = vy = 0.0
    for cx, cy, g, k, a in VORT:
        dx, dy = x - cx, y - cy
        d2 = dx * dx + dy * dy + a * a
        w = a * 2 / d2
        vx += (-g * dy - k * dx) * w
        vy += (g * dx - k * dy) * w
    n = math.hypot(vx, vy) or 1
    return vx / n, vy / n


def streamlines(x0=430, x1=900, y0=0, y1=345, dsep=8.5, h=4.0, seed=4):
    rnd = random.Random(seed)
    cell = dsep
    grid = {}

    def near(x, y, r):
        i, j = int(x // cell), int(y // cell)
        r2 = r * r
        for a in (i - 1, i, i + 1):
            for b in (j - 1, j, j + 1):
                for px, py in grid.get((a, b), ()):
                    if (px - x) ** 2 + (py - y) ** 2 < r2:
                        return True
        return False

    def step(x, y, s):
        vx, vy = vel(x, y)
        mx, my = x + s * vx * h / 2, y + s * vy * h / 2
        vx, vy = vel(mx, my)
        return x + s * vx * h, y + s * vy * h

    def trace(x, y, s):
        out = []
        for n in range(260):
            x, y = step(x, y, s)
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                break
            if near(x, y, dsep * 0.55):
                break
            if any(math.hypot(x - cx, y - cy) < 3 for cx, cy, *_ in VORT):
                break
            if n > 12 and out and math.hypot(x - out[0][0], y - out[0][1]) < h:
                break
            out.append((x, y))
        return out

    lines = []
    for _ in range(9000):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if near(x, y, dsep):
            continue
        fw, bw = trace(x, y, 1), trace(x, y, -1)
        line = bw[::-1] + [(x, y)] + fw
        if len(line) < 10:
            continue
        for p in line:
            grid.setdefault((int(p[0] // cell), int(p[1] // cell)), []).append(p)
        lines.append(line)
    return lines


STREAM = streamlines()


def line_color(c, line):
    mx = sum(p[0] for p in line) / len(line)
    my = sum(p[1] for p in line) / len(line)
    best = min(range(len(VORT)), key=lambda i: math.hypot(mx - VORT[i][0], my - VORT[i][1]) - VORT[i][4])
    d = math.hypot(mx - VORT[best][0], my - VORT[best][1])
    return c["pal"][(int(d / 30) + best) % 4]


def spiral(cx, cy, r, turns=3, rot=0, start=0.15):
    pts = []
    n = int(turns * 28)
    for i in range(n + 1):
        t = i / n
        th = t * turns * 2 * math.pi + rot
        rr = r * (start + (1 - start) * t)
        pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    return pts


def waves(x0, x1, y0, rows, c, amp=12, gap=3.8, seed=1, cols=None):
    rnd = random.Random(seed)
    o = []
    cols = cols or [c["warm"], c["pal"][2], c["warm"], c["pal"][1]]
    ph = rnd.uniform(0, 6)
    for i in range(rows):
        pts = []
        for x in range(int(x0), int(x1) + 1, 6):
            y = y0 + i * gap + amp * math.sin(x / 95 + i * 0.16 + ph) + amp * 0.35 * math.sin(x / 38 + i * 0.3)
            pts.append((x, y))
        o.append(f'<path d="{pts_path(pts)}" fill="none" stroke="{cols[i % len(cols)]}" stroke-width="1.1" opacity="{.5 + .4 * (i % 2)}"/>')
    return "".join(o)


def plus(x, y, s, col, op=0.8):
    return f'<path d="M{x-s} {y}H{x+s}M{x} {y-s}V{y+s}" stroke="{col}" stroke-width="1" opacity="{op}"/>'


def defs(c):
    return f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
<linearGradient id="cardbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['card']}"/><stop offset="1" stop-color="{c['card2']}"/></linearGradient>
<linearGradient id="side" x1="0" x2="1"><stop offset="0" stop-color="{c['bg1']}"/><stop offset=".35" stop-color="{c['bg1']}" stop-opacity=".96"/><stop offset="1" stop-color="{c['bg1']}" stop-opacity="0"/></linearGradient>
</defs>"""


def wrap(w, h, c, body, cls_font=MONO):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{cls_font}">'
        f'{STYLE}{defs(c)}<rect width="{w}" height="{h}" fill="url(#bg)"/>{body}'
        f'<path d="M.5 0V{h}M{w-.5} 0V{h}" stroke="{c["line"]}"/></svg>'
    )


def divider(c, y, w=900):
    pts = [(x, y + 3 * math.sin(x / 38)) for x in range(40, w - 39, 6)]
    d = pts_path(pts)
    return (
        f'<path d="{d}" fill="none" stroke="{c["line"]}" stroke-width="1"/>'
        f'<path class="dots" d="{d}" fill="none" stroke="{c["acc"]}" stroke-width="2.4"/>'
    )


def heading(c, y, idx, label, x=60):
    sp = pts_path(spiral(x, y, 9, 2.4))
    return (
        f'<path d="{sp}" fill="none" stroke="{c["acc"]}" stroke-width="1.5"/>'
        f'<text x="{x+22}" y="{y+4}" font-size="12" letter-spacing="2.2" fill="{c["mute"]}">{idx} /</text>'
        f'<text x="{x+66}" y="{y+4}" font-size="12" font-weight="700" letter-spacing="2.2" fill="{c["fg"]}">{label}</text>'
    )


def corners(c, x, y, w, h, s=7, op=0.9):
    return (
        f'<path d="M{x} {y+s}V{y}H{x+s}M{x+w-s} {y}H{x+w}V{y+s}M{x+w} {y+h-s}V{y+h}H{x+w-s}M{x+s} {y+h}H{x}V{y+h-s}" '
        f'fill="none" stroke="{c["acc"]}" stroke-width="1.3" opacity="{op}"/>'
    )


def hero(c):
    b = "".join(f'<path d="{pts_path(l)}" fill="none" stroke="{line_color(c, l)}" stroke-width="1.15" opacity=".88"/>' for l in STREAM)
    for l in STREAM[::9]:
        b += f'<path class="dots" d="{pts_path(l)}" fill="none" stroke="{c["acc"]}" stroke-width="2.4" opacity=".9"/>'
    b += f'<rect x="400" y="0" width="300" height="400" fill="url(#side)"/>'
    b += waves(0, 900, 372, 12, c, amp=11, gap=3.6)
    for i, (x, y, r) in enumerate([(560, 366, 15), (640, 380, 11), (725, 360, 17), (815, 378, 12), (868, 358, 10)]):
        b += (
            f'<circle cx="{x}" cy="{y}" r="{r+3}" fill="{c["bg1"]}"/>'
            f'<path class="spin{" r" if i % 2 else ""}" d="{pts_path(spiral(x, y, r, 3, i))}" fill="none" stroke="{c["warm"]}" stroke-width="1.4"/>'
        )
    b += (
        f'<path d="{pts_path(spiral(60, 34, 8, 2.4))}" fill="none" stroke="{c["acc"]}" stroke-width="1.4"/>'
        f'<text x="80" y="38" font-size="12" fill="{c["mute"]}">solacode-SC <tspan fill="{c["line"]}">/</tspan> README</text>'
        f'<path d="M40 56H860" stroke="{c["line"]}"/>'
        + plus(40, 56, 4, c["acc"])
        + plus(860, 56, 4, c["acc"])
    )
    b += plus(436, 100, 4, c["mute"], 0.5) + plus(884, 332, 4, c["mute"], 0.5)
    b += f'<text x="868" y="332" font-size="9" text-anchor="end" fill="{c["mute"]}" opacity=".8">r = a·e^(bθ)</text>'
    b += (
        f'<text x="60" y="108" font-size="13" letter-spacing="3" fill="{c["mute"]}">HI, I\'M</text>'
        f'<text x="58" y="160" font-size="42" font-family="{SERIF}" letter-spacing="-.5" fill="{c["fg"]}">{esc(NAME)}</text>'
        f'<text x="60" y="204" font-size="16" font-weight="700" letter-spacing="3" fill="{c["acc"]}">SOFTWARE ENGINEER</text>'
        f'<text x="60" y="246" font-size="13" letter-spacing="1" fill="{c["fg"]}" xml:space="preserve">AI  ·  Math  ·  Newest Technologies</text>'
    )
    for i, t in enumerate(["Building systems, web applications,", "developer tools and intelligent software", "for a better tomorrow."]):
        b += f'<text x="60" y="{290+i*20}" font-size="12.5" fill="{c["mute"]}">{t}</text>'
    b += f'<rect x="60" y="262" width="36" height="2" fill="{c["acc"]}"/>'
    for i, ch in enumerate("夢を築く"):
        b += f'<text x="878" y="{92+i*22}" font-size="14" text-anchor="middle" font-family="{JP}" fill="{c["acc2"]}" opacity=".9">{ch}</text>'
    return wrap(900, 410, c, b)


def button(c, label):
    w = 156
    b = (
        f'<rect x=".75" y=".75" width="{w-1.5}" height="38.5" rx="4" fill="{c["card"]}" stroke="{c["acc2"]}" stroke-opacity=".85" stroke-width="1.2"/>'
        f'<path d="{pts_path(spiral(24, 20, 8, 2.2))}" fill="none" stroke="{c["acc"]}" stroke-width="1.4"/>'
        f'<text x="43" y="24.5" font-size="11.5" font-weight="700" letter-spacing="1.4" fill="{c["fg"]}">{label.upper()}</text>'
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 40" width="{w}" height="{40}" font-family="{MONO}">{b}</svg>'


def about(c):
    b = heading(c, 42, "01", "ABOUT")
    L = [
        "I'm Solayman El Mouden, a software engineer",
        "focused on systems, web technologies,",
        "artificial intelligence and mathematics.",
        "",
        "I enjoy understanding how things work",
        "underneath the abstraction and turning that",
        "knowledge into useful software.",
    ]
    for i, t in enumerate(L):
        b += f'<text x="60" y="{92+i*21}" font-size="13" fill="{c["fg"]}" xml:space="preserve">{t}</text>'
    b += f'<path d="M450 74V246" stroke="{c["line"]}"/>' + plus(450, 74, 4, c["acc"]) + plus(450, 246, 4, c["acc"])
    b += heading(c, 42, "02", "MY JOURNEY", 480)
    for i, (a, t) in enumerate(JOURNEY):
        y = 96 + i * 30
        b += (
            f'<path d="{pts_path(spiral(488, y-4, 6, 2))}" fill="none" stroke="{c["acc"]}" stroke-width="1.3"/>'
            f'<text x="508" y="{y}" font-size="13" fill="{c["fg"]}">{a}</text>'
            f'<path d="M640 {y-4}H664M659 {y-8}L664 {y-4}L659 {y}" fill="none" stroke="{c["acc2"]}"/>'
            f'<text x="682" y="{y}" font-size="13" fill="{c["mute"]}">{t}</text>'
        )
    b += divider(c, 274)
    return wrap(900, 290, c, b)


def skills(c):
    b = heading(c, 40, "03", "TECHNOLOGIES &amp; SKILLS")
    w, g = 125, 14
    for i, (name, mono) in enumerate(SKILLS):
        x = 40 + (i % 6) * (w + g)
        y = 68 + (i // 6) * 66
        b += (
            f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="53" rx="5" fill="{c["card"]}" stroke="{c["line"]}"/>'
            + corners(c, x + 3, y + 3, w - 6, 47, 5, 0.7)
            + f'<text x="{x+w/2}" y="{y+25}" font-size="16" font-weight="700" text-anchor="middle" fill="{c["acc"]}">{esc(mono)}</text>'
            + f'<text x="{x+w/2}" y="{y+43}" font-size="10.5" text-anchor="middle" fill="{c["fg"]}">{esc(name)}</text>'
        )
    b += divider(c, 214)
    return wrap(900, 226, c, b)


def projects_title(c):
    b = (
        heading(c, 36, "04", "SELECTED LIVE PROJECTS")
        + f'<rect x="726" y="21" width="134" height="26" rx="4" fill="{c["card"]}" stroke="{c["acc2"]}" stroke-opacity=".8"/>'
        + f'<circle class="pulse" cx="742" cy="34" r="3.4" fill="{c["live"]}"/>'
        + f'<text x="753" y="37.8" font-size="10" font-weight="700" letter-spacing="1" fill="{c["fg"]}">6 DEPLOYED APPS</text>'
    )
    return wrap(900, 64, c, b)


def motif(c, kind, idx):
    W, H = 268, 76
    p = c["pal"]
    o = []
    if kind == "leetresume":
        # Structured golden-ratio typographic flow converging into AI spark
        for k in range(8):
            pts = [(x, 12 + k * 7.5 + (k - 3.5) * 2.2 * math.sin(x / 46 + k * 0.25)) for x in range(0, W + 1, 4)]
            o.append(f'<path d="{pts_path(pts)}" fill="none" stroke="{p[k % 4]}" stroke-width="1.2" opacity=".82"/>')
        o.append(f'<rect x="172" y="14" width="66" height="48" rx="3" fill="{c["bg1"]}" fill-opacity=".85" stroke="{c["warm"]}" stroke-width="1.2"/>')
        for r in range(4):
            o.append(f'<line x1="182" y1="{25+r*9}" x2="{226 if r != 2 else 212}" y2="{25+r*9}" stroke="{c["acc2"]}" stroke-width="1.4"/>')
        o.append(f'<circle class="pulse" cx="236" cy="18" r="4.5" fill="{c["warm"]}"/>')
    elif kind == "fastdl":
        # High-velocity laminar streamlines + animated travelling data dots
        for k in range(7):
            y = 11 + k * 9
            pts = [(x, y + 3.5 * math.sin(x / 32 + k * 0.6)) for x in range(0, W + 1, 4)]
            d = pts_path(pts)
            o.append(f'<path d="{d}" fill="none" stroke="{p[k % 4]}" stroke-width="1.25" opacity=".85"/>')
            if k in (1, 3, 5):
                o.append(f'<path class="dots" d="{d}" fill="none" stroke="{c["warm"]}" stroke-width="2.4"/>')
        o.append(f'<path d="M124 22L144 38L124 54M136 22L156 38L136 54" fill="none" stroke="{c["warm"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    elif kind == "lazy-equation":
        # Superposed harmonic waves + twin Archimedean phase spirals
        for k, (freq, amp, col) in enumerate([(0.045, 18, p[0]), (0.085, 11, p[1]), (0.13, 7, c["warm"])]):
            pts = [(x, 38 + amp * math.sin(x * freq + k) + 4 * math.sin(x * freq * 2.5)) for x in range(0, W + 1, 3)]
            o.append(f'<path d="{pts_path(pts)}" fill="none" stroke="{col}" stroke-width="1.35"/>')
        o.append(f'<path class="spin" d="{pts_path(spiral(212, 38, 24, 3.5))}" fill="none" stroke="{c["warm"]}" stroke-width="1.3"/>')
    elif kind == "xstudio":
        # 3x3 modular 9-utility PDF matrix with glowing active nodes
        for col in range(3):
            for row in range(3):
                rx, ry = 148 + col * 34, 11 + row * 19
                active = (col + row) % 3 == 0
                o.append(
                    f'<rect x="{rx}" y="{ry}" width="26" height="14" rx="2.5" '
                    f'fill="{c["warm"] if active else c["card"]}" fill-opacity="{.85 if active else .9}" stroke="{p[(col+row)%4]}" stroke-width="1.1"/>'
                )
        for k in range(5):
            o.append(f'<path d="M12 {14+k*12} C66 {14+k*12} 90 38 140 {18+k*10}" fill="none" stroke="{p[k%4]}" stroke-width="1.15" opacity=".75"/>')
    elif kind == "md-converter":
        # Converging document streams -> crisp Markdown "#" token bars
        for dy in (-20, -10, 0, 10, 20):
            d = f"M8 {38+dy} C76 {38+dy} 94 38 148 38"
            o.append(f'<path d="{d}" fill="none" stroke="{p[abs(dy)//10 % 4]}" stroke-width="1.25" opacity=".85"/>')
        o.append(f'<path class="dots" d="M8 38H154" fill="none" stroke="{c["warm"]}" stroke-width="2.6"/>')
        o.append(f'<text x="174" y="47" font-size="30" font-weight="700" fill="{c["warm"]}">#</text>')
        for r in range(3):
            o.append(f'<rect x="204" y="{20+r*14}" width="{48-r*8}" height="6" rx="2" fill="{p[r]}" opacity=".85"/>')
    else:  # chemify
        # Atomic orbital ellipses + hexagonal molecular lattice
        cx, cy = 192, 38
        for rot in (0, 60, -60):
            o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="42" ry="15" transform="rotate({rot} {cx} {cy})" fill="none" stroke="{p[(rot//60)%4]}" stroke-width="1.25" opacity=".88"/>')
        o.append(f'<circle class="pulse" cx="{cx}" cy="{cy}" r="5.5" fill="{c["warm"]}"/>')
        # Hex lattice on left
        for hx, hy in ((46, 38), (82, 24), (82, 52), (118, 38)):
            hpts = [(hx + 16 * math.cos(math.radians(a)), hy + 16 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
            o.append(f'<polygon points="{" ".join(f"{f1(px)},{f1(py)}" for px, py in hpts)}" fill="none" stroke="{p[1]}" stroke-width="1.1" opacity=".8"/>')
            o.append(f'<circle cx="{hx}" cy="{hy}" r="2.2" fill="{c["warm"]}"/>')
    return "".join(o)


def card(c, idx, proj):
    w, h = 288, 228
    d1, d2 = proj["description_lines"][:2]
    tags = proj.get("card_tags", proj["tags"][:3])
    b = (
        f'<defs><clipPath id="cl{idx}"><rect x="10" y="10" width="268" height="76" rx="5"/></clipPath></defs>'
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="8" fill="url(#cardbg)" stroke="{c["line"]}" stroke-width="1.2"/>'
        + corners(c, 5, 5, w - 10, h - 10, 8, 0.85)
        + f'<rect x="10" y="10" width="268" height="76" rx="5" fill="{c["bg1"]}" stroke="{c["line"]}" stroke-opacity=".7"/>'
        + f'<g transform="translate(10 10)" clip-path="url(#cl{idx})">{motif(c, proj["id"], idx)}</g>'
        # Top-left index & top-right LIVE badge
        + f'<rect x="16" y="16" width="40" height="18" rx="3" fill="{c["bg1"]}" fill-opacity=".86" stroke="{c["line"]}"/>'
        + f'<text x="36" y="28.3" text-anchor="middle" font-size="9" font-weight="700" fill="{c["acc"]}">N°{esc(proj["number"])}</text>'
        + f'<rect x="216" y="16" width="56" height="18" rx="3" fill="{c["bg1"]}" fill-opacity=".88" stroke="{c["live"]}" stroke-opacity=".8"/>'
        + f'<circle class="pulse" cx="227" cy="25" r="2.8" fill="{c["live"]}"/>'
        + f'<text x="235" y="28.3" font-size="8.8" font-weight="700" letter-spacing=".8" fill="{c["fg"]}">LIVE</text>'
        # Title & description
        + f'<text x="16" y="113" font-size="16" font-weight="700" font-family="{SERIF}" fill="{c["fg"]}">{esc(proj["title"])}</text>'
        + f'<text x="16" y="133" font-size="11" fill="{c["mute"]}">{esc(d1)}</text>'
        + f'<text x="16" y="148" font-size="11" fill="{c["mute"]}">{esc(d2)}</text>'
    )
    x = 16
    for t in tags:
        cw = len(t) * 6.0 + 16
        if x + cw > w - 14:
            break
        b += (
            f'<rect x="{f1(x)}" y="161" width="{f1(cw)}" height="19" rx="3.5" fill="{c["pill"]}" stroke="{c["line"]}"/>'
            f'<text x="{f1(x+cw/2)}" y="173.8" font-size="9" font-weight="600" text-anchor="middle" fill="{c["acc2"]}">{esc(t)}</text>'
        )
        x += cw + 6

    b += (
        f'<line x1="16" y1="194" x2="{w-16}" y2="194" stroke="{c["line"]}" stroke-opacity=".7"/>'
        f'<text x="16" y="213" font-size="9.3" fill="{c["mute"]}">{esc(proj["display_url"])}</text>'
        f'<text x="{w-16}" y="213" text-anchor="end" font-size="9.5" font-weight="700" fill="{c["acc"]}">OPEN ↗</text>'
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{MONO}">{STYLE}{defs(c)}{b}</svg>'


def footer(c):
    b = waves(0, 900, 78, 13, c, amp=10, gap=3.5, seed=5)
    for i, (x, y, r) in enumerate([(90, 70, 14), (210, 82, 10), (690, 72, 12), (800, 84, 16), (860, 68, 9)]):
        b += (
            f'<circle cx="{x}" cy="{y}" r="{r+3}" fill="{c["bg1"]}"/>'
            f'<path class="spin{" r" if i % 2 else ""}" d="{pts_path(spiral(x, y, r, 3, i))}" fill="none" stroke="{c["warm"]}" stroke-width="1.4"/>'
        )
    b += f'<rect x="270" y="0" width="360" height="74" fill="{c["bg1"]}" opacity=".9"/>'
    b += (
        f'<text x="450" y="34" font-size="14" font-weight="700" letter-spacing="3" text-anchor="middle" fill="{c["acc"]}" xml:space="preserve">BUILD  ·  EXPLORE  ·  UNDERSTAND</text>'
        f'<text x="450" y="56" font-size="10.5" letter-spacing="1" text-anchor="middle" fill="{c["mute"]}" xml:space="preserve">Software Engineering · Systems · AI · Mathematics</text>'
    )
    return wrap(900, 130, c, b)


def save(name, theme, svg_text):
    svg_text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", svg_text)
    (OUT / f"{name}-{theme}.svg").write_text(svg_text, encoding="utf-8")


def main():
    for old in OUT.glob("card-*.svg"):
        old.unlink()

    for th, c in THEMES.items():
        save("hero", th, hero(c))
        save("about", th, about(c))
        save("skills", th, skills(c))
        save("projects-title", th, projects_title(c))
        save("footer", th, footer(c))
        for lbl in ("GitHub", "LinkedIn", "Portfolio"):
            save(f"btn-{lbl.lower()}", th, button(c, lbl))
        for i, proj in enumerate(PROJECTS):
            save(f'card-{proj["id"]}', th, card(c, i, proj))

    def pic(name, alt, width=None, href=None):
        w = f' width="{width}"' if width else ""
        p = (
            f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
            f'  <img alt="{html.escape(alt)}" src="assets/{name}-dark.svg"{w}>\n</picture>'
        )
        return f'<a href="{href}">{p}</a>' if href else p

    def card_row(items):
        return "\n".join(
            pic(f'card-{p["id"]}', f'{p["title"]} — {p["description"]}', "32%", p["live_url"]) for p in items
        )

    parts = [
        pic("hero", f"{NAME} — Software Engineer. AI, Math, Newest Technologies.", "100%"),
        "<br>\n"
        + "&nbsp;\n".join(
            pic(f"btn-{l.lower()}", l, href=u) for l, u in (("GitHub", GITHUB), ("LinkedIn", LINKEDIN), ("Portfolio", PORTFOLIO))
        ),
        pic("about", "About and journey", "100%"),
        pic("skills", "Technologies and skills", "100%"),
        pic("projects-title", "Selected live projects", "100%"),
        card_row(PROJECTS[:3]),
        card_row(PROJECTS[3:6]),
        pic("footer", "Build, Explore, Understand", "100%"),
        f'<sub><a href="{PORTFOLIO}">{PORTFOLIO_DISPLAY}</a> &nbsp;·&nbsp; <a href="{LINKEDIN}">LinkedIn</a> &nbsp;·&nbsp; <a href="{GITHUB}">GitHub</a></sub>',
    ]
    (HERE / "README.md").write_text('<div align="center">\n\n' + "\n\n".join(parts) + "\n\n</div>\n", encoding="utf-8")
    print(f"[Flow Field & Swirl] Generated 3x2 live portfolio assets ({len(STREAM)} streamlines) & README.md")


if __name__ == "__main__":
    main()
