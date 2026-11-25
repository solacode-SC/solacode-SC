#!/usr/bin/env python3
"""Ink-scroll edition — Enhanced 3x2 Live Album-Leaf Portfolio Edition.
Reads central data from ../../profile-data.json. Hand-painted hanging scroll
with tapered ink strokes, vermilion seals, xuan-paper fibre texture, and
6 symmetrical 3x2 live project album-leaf cards."""
import base64
import html
import io
import json
import math
import os
import random
import re
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "assets"
OUT.mkdir(parents=True, exist_ok=True)
ART = Image.open(HERE / "art" / "source.jpg")
DATA = json.loads((ROOT / "profile-data.json").read_text(encoding="utf-8"))

SERIF = "Georgia,'Iowan Old Style','Palatino Linotype','Book Antiqua','DejaVu Serif',serif"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Consolas,Menlo,monospace"
CJK = "'KaiTi','STKaiti','Kaiti SC','AR PL UKai CN','Noto Serif SC','Songti SC','SimSun',serif"

THEMES = {
    "light": dict(
        bg1="#f3e9cd",
        bg2="#e4d4a9",
        fg="#26211b",
        ink="#23201c",
        mute="#635746",
        indigo="#29486f",
        verm="#bf2a22",
        live="#287a4e",
        line="#b9a77a",
        card="#f8f0d6",
        mount="#b3c3ca",
        mount2="#8ea5b2",
        green="#3a6b4a",
        paper="#f6edd2",
        fibre="0 0 0 0 .45  0 0 0 0 .33  0 0 0 0 .15  0 0 0 .5 0",
        bloom=["#bf2a22", "#f8f1df", "#e9a8a0"],
        petal=["#f4d6d0", "#e9a8a0", "#bf2a22"],
    ),
    "dark": dict(
        bg1="#181d28",
        bg2="#0d1017",
        fg="#efe5cb",
        ink="#d9cfb6",
        mute="#a99f88",
        indigo="#93b3d9",
        verm="#d6402f",
        live="#68d391",
        line="#3b4662",
        card="#1b2130",
        mount="#2a3c55",
        mount2="#42597a",
        green="#6aa77e",
        paper="#efe5cb",
        fibre="0 0 0 0 .9  0 0 0 0 .85  0 0 0 0 .7  0 0 0 .22 0",
        bloom=["#d6402f", "#efe3cf", "#d99a96"],
        petal=["#efe3cf", "#d99a96", "#d6402f"],
    ),
}

USE_CJK = True


def cj(zh, latin=""):
    return zh if USE_CJK else latin


def esc(s):
    return html.escape(str(s), quote=False)


GITHUB = DATA["links"]["github"]
LINKEDIN = DATA["links"]["linkedin"]
PORTFOLIO = DATA["links"]["portfolio"]
PORTFOLIO_DISPLAY = DATA["links"]["portfolio_display"]
NAME = DATA["profile"]["name"]

JOURNEY = [
    ("C / C++", "Systems"),
    ("Python", "Backend & AI"),
    ("TypeScript", "Web & Tools"),
    ("Docker", "Infrastructure"),
    ("Linux", "DevOps"),
]
SKILLS = [(s["name"], s["short"]) for s in DATA["skills"]]
NUM_HEAD = [cj(a, b) for a, b in zip("壹貳參肆", ["I", "II", "III", "IV"])]
NUM_CARD = [cj(a, str(i + 1)) for i, a in enumerate("一二三四五六")]

# 6 landscape crops from art/source.jpg (736x1104)
CROPS = [
    (120, 860, 390, 962),
    (270, 385, 540, 487),
    (140, 440, 410, 542),
    (270, 785, 540, 887),
    (100, 140, 370, 242),
    (456, 365, 726, 467),
]
PROJECTS = DATA["projects"]


def crop64(box, size, q=82):
    im = ART.crop(box).resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def full64(size, q=80):
    im = ART.resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


STYLE = """<style>
.sway{transform-origin:710px 8px;animation:sway 11s ease-in-out infinite alternate}
@keyframes sway{from{transform:rotate(-.45deg)}to{transform:rotate(.45deg)}}
.pfall{animation:pfall linear infinite}
@keyframes pfall{from{transform:translateY(-30px)}to{transform:translateY(560px)}}
.psway{transform-box:fill-box;transform-origin:center;animation:psway ease-in-out infinite alternate}
@keyframes psway{from{transform:translateX(-26px) rotate(-30deg)}to{transform:translateX(26px) rotate(30deg)}}
.rip{transform-box:fill-box;transform-origin:center;animation:rip 9s ease-out infinite;opacity:0}
@keyframes rip{0%{transform:scale(.2);opacity:0}15%{opacity:.7}100%{transform:scale(1.6);opacity:0}}
.sun{animation:sun 12s ease-in-out infinite}
@keyframes sun{0%,100%{opacity:.05}50%{opacity:.34}}
.mist{animation:mist 40s ease-in-out infinite alternate}
@keyframes mist{from{transform:translateX(-40px)}to{transform:translateX(40px)}}
.wave{animation:wave 26s linear infinite}
@keyframes wave{to{transform:translateX(-48px)}}
.pulse{animation:pl 2.8s ease-in-out infinite}
@keyframes pl{0%,100%{opacity:1}50%{opacity:.35}}
@media (prefers-reduced-motion:reduce){.sway,.pfall,.psway,.rip,.sun,.mist,.wave,.pulse{animation:none}}
</style>"""


def f1(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def defs(c):
    return f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".65" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="{c['line']}" stop-opacity=".28"/></radialGradient>
<radialGradient id="sunglow"><stop offset="0" stop-color="#ff6a4a" stop-opacity=".9"/><stop offset="1" stop-color="#ff6a4a" stop-opacity="0"/></radialGradient>
<filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .4" numOctaves="3" seed="5"/><feColorMatrix values="{c['fibre']}"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 .3  0 0 0 0 .22  0 0 0 0 .1  0 0 0 .13 0"/></filter>
<filter id="rough" x="-6%" y="-6%" width="112%" height="112%"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="3" seed="7" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="3.4" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="wob" x="-4%" y="-20%" width="108%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".09" numOctaves="2" seed="3" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="1.6" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="paint" x="-4%" y="-4%" width="108%" height="108%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="3" seed="2" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="2.2" xChannelSelector="R" yChannelSelector="G" result="d"/><feColorMatrix in="d" type="saturate" values=".92"/></filter>
<pattern id="sei" width="24" height="12" patternUnits="userSpaceOnUse"><g fill="none" stroke="{c['mount2']}" stroke-width=".8"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="4"/><circle cx="0" cy="6" r="10"/><circle cx="0" cy="6" r="7"/><circle cx="0" cy="6" r="4"/><circle cx="24" cy="6" r="10"/><circle cx="24" cy="6" r="7"/><circle cx="24" cy="6" r="4"/></g></pattern>
</defs>"""


def wrap(w, h, c, body, edge=True):
    side = f'<path d="M.5 0V{h}M{w-.5} 0V{h}" stroke="{c["line"]}"/>' if edge else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{SERIF}">'
        f'{STYLE}{defs(c)}<rect width="{w}" height="{h}" fill="url(#bg)"/>'
        f'<rect width="{w}" height="{h}" filter="url(#paper)"/><rect width="{w}" height="{h}" filter="url(#grain)"/>'
        f'<rect width="{w}" height="{h}" fill="url(#vig)"/>{body}{side}</svg>'
    )


def taper(pts, w0, w1, r):
    n = len(pts)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        w = (w0 * (1 - t) + w1 * t) * r.uniform(0.85, 1.15)
        xa, ya = pts[max(i - 1, 0)]
        xb, yb = pts[min(i + 1, n - 1)]
        dx, dy = xb - xa, yb - ya
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((x + nx * w / 2, y + ny * w / 2))
        R.append((x - nx * w / 2, y - ny * w / 2))
    return "M" + "L".join(f"{f1(a)} {f1(b)}" for a, b in L + R[::-1]) + "Z"


def curve(x0, y0, x1, y1, bend, n=14, r=None, jit=0.5):
    r = r or random.Random(1)
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + bend * math.sin(t * math.pi)
        pts.append((x + r.uniform(-jit, jit), y + r.uniform(-jit, jit)))
    return pts


def brush(c, x0, y0, x1, y1, w0=3, w1=0.5, bend=0, seed=1, col=None, op=0.9):
    r = random.Random(seed)
    return f'<path d="{taper(curve(x0, y0, x1, y1, bend, 16, r), w0, w1, r)}" fill="{col or c["ink"]}" opacity="{op}" filter="url(#wob)"/>'


def blossom(c, x, y, R, r, col=None):
    col = col or r.choice(c["bloom"])
    o = []
    stroke = c["verm"] if col != c["bloom"][0] else c["ink"]
    rot = r.uniform(0, 72)
    for i in range(5):
        a = math.radians(rot + i * 72)
        o.append(
            f'<circle cx="{f1(x+R*.55*math.cos(a))}" cy="{f1(y+R*.55*math.sin(a))}" r="{f1(R*.5)}" fill="{col}" stroke="{stroke}" stroke-opacity=".55" stroke-width=".6"/>'
        )
    o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(R*.2)}" fill="#e0b13a"/>')
    return "".join(o)


def branch(c, x0, y0, x1, y1, seed=1, n_blooms=7, w0=5, bend=-14, sparse=False):
    r = random.Random(seed)
    o = []
    main_pts = curve(x0, y0, x1, y1, bend, 22, r, 0.8)
    o.append(f'<path d="{taper(main_pts, w0, 0.9, r)}" fill="{c["ink"]}" opacity=".92" filter="url(#wob)"/>')
    tips = [main_pts[-1]]
    for k in range(5 if not sparse else 3):
        i = int(len(main_pts) * (0.15 + k * 0.17))
        bx, by = main_pts[i]
        ang = math.radians((-62 if k % 2 == 0 else 58) + r.uniform(-12, 12)) + math.atan2(y1 - y0, x1 - x0)
        ln = r.uniform(22, 44)
        ex, ey = bx + ln * math.cos(ang), by + ln * math.sin(ang)
        tw = curve(bx, by, ex, ey, r.uniform(-5, 5), 8, r, 0.5)
        o.append(f'<path d="{taper(tw, 2.4, 0.5, r)}" fill="{c["ink"]}" opacity=".9" filter="url(#wob)"/>')
        tips.append((ex, ey))
    for tx, ty in tips[:n_blooms]:
        o.append(blossom(c, tx, ty, r.uniform(4.2, 6.2), r))
    for _ in range(n_blooms // 2):
        i = r.randint(3, len(main_pts) - 3)
        bx, by = main_pts[i]
        o.append(f'<circle cx="{f1(bx+r.uniform(-6,6))}" cy="{f1(by+r.uniform(-9,9))}" r="{r.uniform(1.6,2.6):.1f}" fill="{c["verm"]}"/>')
    return "".join(o)


def divider(c, y, seed=1):
    return branch(c, 40, y + 6, 860, y - 4, seed, 6, 2.4, -8, True)


def hand_text(txt, x, y, size, fill, seed, weight="400", ls=0, extra=""):
    r = random.Random(seed)
    offs = [r.uniform(-1.0, 1.0) for _ in txt]
    dys = [offs[0]] + [offs[i] - offs[i - 1] for i in range(1, len(txt))]
    rots = [f1(r.uniform(-1.2, 1.2)) for _ in txt]
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" letter-spacing="{ls}" '
        f'rotate="{" ".join(rots)}" dy="{" ".join(f1(d) for d in dys)}" {extra}>{esc(txt)}</text>'
    )


def seal(c, x, y, s, glyph, seed=1, fs=None, rot=None):
    r = random.Random(seed)
    rot = rot if rot is not None else r.uniform(-3, 3)
    fs = fs or s * 0.6
    return (
        f'<g transform="rotate({f1(rot)} {f1(x+s/2)} {f1(y+s/2)})" filter="url(#rough)"><rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c["verm"]}"/>'
        f'<rect x="{x+s*.07}" y="{y+s*.07}" width="{s*.86}" height="{s*.86}" fill="none" stroke="{c["paper"]}" stroke-opacity=".75" stroke-width="{max(1, s*.035):.1f}"/>'
        f'<text x="{x+s/2}" y="{y+s*.72}" font-size="{f1(fs)}" font-family="{CJK}" font-weight="700" text-anchor="middle" fill="{c["paper"]}">{glyph}</text></g>'
    )


def heading(c, y, idx, label, x=60):
    return (
        seal(c, x, y - 14, 24, NUM_HEAD[idx], idx + 3, 16, 0)
        + hand_text(label, x + 36, y + 5, 15, c["fg"], idx + 20, "700", 3)
        + brush(c, x, y + 18, x + 320, y + 20, 2.6, 0.4, 1.5, idx + 40, c["indigo"], 0.75)
    )


def petals(c, n, xr, seed=3):
    r = random.Random(seed)
    o = []
    for _ in range(n):
        x = r.uniform(*xr)
        s = r.uniform(0.7, 1.2)
        col = r.choice(c["petal"])
        d = r.uniform(34, 56)
        sd = r.uniform(5, 9)
        o.append(
            f'<g transform="translate({f1(x)} 0)"><g class="pfall" style="animation-duration:{d:.1f}s;animation-delay:{-r.uniform(0, d):.1f}s">'
            f'<g class="psway" style="animation-duration:{sd:.1f}s;animation-delay:{-r.uniform(0, sd):.1f}s">'
            f'<path transform="rotate({r.uniform(0, 180):.0f}) scale({s:.2f})" d="M0 -7C6 -7 7 3 0 8C-7 3 -6 -7 0 -7Z" fill="{col}" opacity=".85"/></g></g></g>'
        )
    return "".join(o)


def cloud(c, x, y, k, col, op=0.2):
    cs = [(0, 0, 16), (20, -8, 20), (44, -2, 17), (62, 6, 12), (-16, 8, 11)]
    o = "".join(f'<circle cx="{x+a*k:.1f}" cy="{y+b*k:.1f}" r="{r*k:.1f}"/>' for a, b, r in cs)
    sp = "M" + "L".join(f"{f1(x+20*k+(2+t*.9)*math.cos(t*.6)*k)} {f1(y-8*k+(2+t*.9)*math.sin(t*.6)*k)}" for t in range(0, 22))
    return f'<g class="mist" fill="{col}" opacity="{op}">{o}</g><path class="mist" d="{sp}" fill="none" stroke="{col}" stroke-width="1.4" opacity="{op*2}"/>'


def hero(c):
    W, H = 900, 540
    img = full64((496, 744), 80)
    av = crop64((230, 450, 330, 550), (64, 64))
    b = branch(c, -10, 520, 340, 430, 4, 8, 6, -20)
    b += cloud(c, 380, 66, 0.8, c["indigo"], 0.16) + cloud(c, 420, 470, 0.7, c["indigo"], 0.13)
    b += (
        f'<defs><clipPath id="av"><circle cx="64" cy="48" r="14"/></clipPath></defs>'
        f'<image x="50" y="34" width="28" height="28" clip-path="url(#av)" href="{av}" xlink:href="{av}"/>'
        f'<circle cx="64" cy="48" r="14" fill="none" stroke="{c["ink"]}" stroke-width="1.4" filter="url(#wob)"/>'
        f'<text x="88" y="52" font-size="12" font-family="{MONO}" fill="{c["mute"]}">solacode-SC <tspan fill="{c["verm"]}">/</tspan> README</text>'
    )
    b += (
        brush(c, 60, 124, 84, 124, 2.4, 0.5, 0, 5, c["verm"])
        + f'<text x="94" y="129" font-size="13" letter-spacing="4" fill="{c["mute"]}">HI, I\'M</text>'
        + hand_text(NAME, 58, 186, 36, c["ink"], 7)
        + hand_text("SOFTWARE ENGINEER", 60, 232, 15, c["indigo"], 8, "700", 5)
        + f'<text x="60" y="272" font-size="14" letter-spacing="1.5" fill="{c["fg"]}" xml:space="preserve">AI  ·  Math  ·  Newest Technologies</text>'
        + brush(c, 60, 292, 250, 294, 3, 0.4, 2, 12, c["ink"], 0.8)
    )
    for i, t in enumerate(["Building systems, web applications,", "developer tools and intelligent software", "for a better tomorrow."]):
        b += f'<text x="60" y="{328+i*23}" font-size="14" font-style="italic" fill="{c["mute"]}">{t}</text>'
    for i, ch in enumerate(cj("築夢", "")):
        b += f'<text x="516" y="{176+i*58}" font-size="46" font-family="{CJK}" font-weight="700" text-anchor="middle" fill="{c["ink"]}" opacity=".9" filter="url(#wob)">{ch}</text>'
    b += seal(c, 494, 300, 44, cj("码", "SC"), 3)
    px, py, pw, ph = 586, 92, 248, 372
    sx = pw / 736
    sun = (px + 365 * sx, py + 355 * sx)
    lake = (px + 372 * sx, py + 610 * sx)
    sc = (
        f'<g class="sway">'
        f'<path d="M710 8L572 40M710 8L848 40" stroke="{c["ink"]}" stroke-width="1.2"/><circle cx="710" cy="8" r="3.2" fill="none" stroke="{c["ink"]}" stroke-width="1.4"/>'
        f'<rect x="562" y="36" width="296" height="10" rx="5" fill="{c["ink"]}"/><circle cx="560" cy="41" r="6" fill="{c["verm"]}"/><circle cx="860" cy="41" r="6" fill="{c["verm"]}"/>'
        f'<rect x="570" y="46" width="280" height="452" fill="{c["mount"]}" stroke="{c["ink"]}" stroke-width="1"/><rect x="570" y="46" width="280" height="452" fill="url(#sei)"/>'
        f'<rect x="576" y="52" width="268" height="440" fill="none" stroke="{c["paper"]}" stroke-opacity=".7"/>'
        f'<rect x="{px-8}" y="{py-8}" width="{pw+16}" height="{ph+16}" fill="{c["paper"]}" stroke="{c["ink"]}" stroke-opacity=".55"/>'
        f'<defs><clipPath id="pw"><rect x="{px}" y="{py}" width="{pw}" height="{ph}"/></clipPath></defs>'
        f'<g clip-path="url(#pw)"><image x="{px}" y="{py}" width="{pw}" height="{ph}" href="{img}" xlink:href="{img}" filter="url(#paint)"/>'
        f'<circle class="sun" cx="{f1(sun[0])}" cy="{f1(sun[1])}" r="52" fill="url(#sunglow)"/>'
        f'<g fill="none" stroke="#fff" stroke-width="1.2"><ellipse class="rip" cx="{f1(lake[0])}" cy="{f1(lake[1])}" rx="46" ry="10"/><ellipse class="rip" style="animation-delay:-4.5s" cx="{f1(lake[0])}" cy="{f1(lake[1])}" rx="46" ry="10"/></g>'
        f'<g class="mist" opacity=".5"><ellipse cx="{px+90}" cy="{py+250}" rx="70" ry="9" fill="#fff" opacity=".35"/><ellipse cx="{px+190}" cy="{py+300}" rx="60" ry="7" fill="#fff" opacity=".3"/></g>'
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#c9b27a" opacity=".12" style="mix-blend-mode:multiply"/></g>'
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="{c["ink"]}" stroke-width="1.2" filter="url(#wob)"/>'
    )
    sc += (
        f'<text x="{px+14}" y="{py+ph+30}" font-size="13" font-family="{CJK}" letter-spacing="6" fill="{c["ink"]}" opacity=".85">{cj("靜水流深", "")}</text>'
        + seal(c, px + pw - 30, py + ph + 14, 24, cj("码", "SC"), 11, 13, 2)
        + f'<rect x="562" y="498" width="296" height="12" rx="6" fill="{c["ink"]}"/><circle cx="560" cy="504" r="6" fill="{c["verm"]}"/><circle cx="860" cy="504" r="6" fill="{c["verm"]}"/></g>'
    )
    b += sc + petals(c, 9, (300, 860), 6) + divider(c, 526, 3)
    return wrap(W, H, c, b)


def button(c, label):
    w = 156
    glyph = {"GitHub": cj("码", "G"), "LinkedIn": cj("链", "in"), "Portfolio": cj("作", "P")}[label]
    b = (
        f'<rect x="2" y="2" width="{w-4}" height="36" fill="{c["card"]}" stroke="{c["ink"]}" stroke-width="1.4" filter="url(#wob)"/>'
        f'<rect x="8" y="9" width="22" height="22" fill="{c["verm"]}" filter="url(#rough)"/>'
        f'<text x="19" y="25.5" font-size="14" font-family="{CJK}" font-weight="700" text-anchor="middle" fill="{c["paper"]}">{glyph}</text>'
        f'<text x="41" y="24.5" font-size="12" font-weight="700" letter-spacing="2" fill="{c["fg"]}">{label.upper()}</text>'
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 40" width="{w}" height="40" font-family="{SERIF}">{defs(c)}{b}</svg>'


def about(c):
    b = heading(c, 42, 0, "ABOUT")
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
        b += f'<text x="60" y="{92+i*23}" font-size="14" fill="{c["fg"]}" xml:space="preserve">{t}</text>'
    b += brush(c, 452, 74, 452, 246, 1.8, 0.6, 4, 21, c["ink"], 0.55)
    b += heading(c, 42, 1, "MY JOURNEY", 480)
    for i, (a, t) in enumerate(JOURNEY):
        y = 98 + i * 30
        b += (
            f'<circle cx="490" cy="{y-4}" r="3.6" fill="{c["verm"]}" filter="url(#wob)"/>'
            f'<text x="506" y="{y}" font-size="14" fill="{c["fg"]}">{a}</text>'
            + brush(c, 612, y - 4, 690, y - 5, 1.8, 0.4, 1, 30 + i, c["ink"], 0.6)
            + f'<text x="702" y="{y}" font-size="14" font-style="italic" fill="{c["mute"]}">{t}</text>'
        )
    b += divider(c, 276, 5) + petals(c, 3, (500, 860), 15)
    return wrap(900, 296, c, b)


def skills(c):
    b = heading(c, 40, 2, "TECHNOLOGIES &amp; SKILLS")
    r = random.Random(4)
    for i, (name, mono) in enumerate(SKILLS):
        cx = 40 + 68.3 + (i % 6) * 136.7
        cy = 94 + (i // 6) * 100
        s = 62
        b += (
            f'<g transform="rotate({r.uniform(-2.5, 2.5):.1f} {f1(cx)} {cy})" filter="url(#rough)"><rect x="{f1(cx-s/2)}" y="{cy-s/2}" width="{s}" height="{s}" fill="{c["verm"]}"/>'
            f'<rect x="{f1(cx-s/2+5)}" y="{cy-s/2+5}" width="{s-10}" height="{s-10}" fill="none" stroke="{c["paper"]}" stroke-opacity=".7" stroke-width="1.6"/>'
            f'<text x="{f1(cx)}" y="{cy+8}" font-size="22" font-weight="700" text-anchor="middle" fill="{c["paper"]}">{esc(mono)}</text></g>'
            f'<text x="{f1(cx)}" y="{cy+50}" font-size="12" font-style="italic" text-anchor="middle" fill="{c["fg"]}">{esc(name)}</text>'
        )
    b += divider(c, 272, 6) + petals(c, 3, (60, 840), 16)
    return wrap(900, 292, c, b)


def projects_title(c):
    b = (
        heading(c, 34, 3, "SELECTED LIVE PROJECTS")
        + f'<rect x="720" y="19" width="136" height="26" fill="{c["card"]}" stroke="{c["ink"]}" stroke-opacity=".65" filter="url(#wob)"/>'
        + f'<circle class="pulse" cx="737" cy="32" r="3.4" fill="{c["live"]}"/>'
        + f'<text x="748" y="36" font-family="{MONO}" font-size="10" font-weight="700" letter-spacing="1" fill="{c["fg"]}">6 DEPLOYED APPS</text>'
    )
    return wrap(900, 68, c, b)


def card(c, idx, proj, box):
    w, h = 288, 248
    r = random.Random(idx + 50)
    img = crop64(box, (520, 196), 82)
    d1, d2 = proj["description_lines"][:2]
    tags = proj.get("card_tags", proj["tags"][:3])
    b = (
        f'<rect x="3" y="3" width="{w-6}" height="{h-6}" fill="{c["card"]}" stroke="{c["ink"]}" stroke-width="1.6" filter="url(#wob)"/>'
        f'<rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="{c["ink"]}" stroke-opacity=".32" filter="url(#wob)"/>'
        f'<image x="16" y="16" width="256" height="96" preserveAspectRatio="xMidYMid slice" href="{img}" xlink:href="{img}" filter="url(#paint)"/>'
        f'<rect x="16" y="16" width="256" height="96" fill="#c9b27a" opacity=".12" style="mix-blend-mode:multiply"/>'
        f'<rect x="16" y="16" width="256" height="96" fill="none" stroke="{c["ink"]}" stroke-opacity=".45" stroke-width="1"/>'
        # Vermilion kanji seal top-right
        + seal(c, 242, 10, 26, NUM_CARD[idx], idx + 60, 17, r.uniform(-3, 3))
        # Subtle LIVE stamp top-left on painting
        + f'<rect x="22" y="22" width="54" height="19" fill="{c["bg1"]}" fill-opacity=".88" stroke="{c["live"]}" stroke-opacity=".85"/>'
        + f'<circle class="pulse" cx="33" cy="31.5" r="2.8" fill="{c["live"]}"/>'
        + f'<text x="41" y="34.8" font-family="{MONO}" font-size="8.8" font-weight="700" letter-spacing=".8" fill="{c["fg"]}">LIVE</text>'
        # Title & description
        + hand_text(proj["title"], 18, 138, 17, c["ink"], idx + 70, "700")
        + f'<text x="18" y="159" font-size="12" font-style="italic" fill="{c["mute"]}">{esc(d1)}</text>'
        + f'<text x="18" y="175" font-size="12" font-style="italic" fill="{c["mute"]}">{esc(d2)}</text>'
    )
    x = 18
    for t in tags:
        cw = len(t) * 5.9 + 14
        if x + cw > w - 16:
            break
        b += (
            f'<rect x="{f1(x)}" y="187" width="{f1(cw)}" height="19" fill="none" stroke="{c["indigo"]}" stroke-opacity=".82" filter="url(#wob)"/>'
            f'<text x="{f1(x+cw/2)}" y="199.5" font-size="9" font-family="{MONO}" font-weight="600" text-anchor="middle" fill="{c["indigo"]}">{esc(t)}</text>'
        )
        x += cw + 6

    b += (
        brush(c, 18, 217, w - 18, 217, 1.3, 0.4, 0.5, idx + 90, c["line"], 0.75)
        + f'<text x="18" y="234" font-family="{MONO}" font-size="9.3" fill="{c["mute"]}">{esc(proj["display_url"])}</text>'
        + f'<text x="{w-18}" y="234" text-anchor="end" font-family="{MONO}" font-size="9.5" font-weight="700" fill="{c["verm"]}">OPEN ↗</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{SERIF}">{STYLE}{defs(c)}{b}</svg>'
    )


def seigaiha(c, y0, rows, cols=21):
    o = []
    fills = [c["indigo"], c["paper"], c["indigo"], c["paper"]]
    for rr in range(rows):
        for cc in range(-1, cols):
            cx = cc * 48 + (24 if rr % 2 else 0)
            cy = y0 + rr * 13
            for rad, f in zip((24, 18, 12, 6), fills):
                o.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{f}" stroke="{c["ink"]}" stroke-opacity=".35" stroke-width=".6"/>')
    return f'<g class="wave" opacity=".92">{"".join(o)}</g>'


def footer(c):
    b = branch(c, 910, 6, 600, 58, 8, 8, 5, 10)
    b += hand_text("BUILD  ·  EXPLORE  ·  UNDERSTAND", 60, 74, 20, c["ink"], 31, "700", 3, 'xml:space="preserve"')
    b += brush(c, 60, 90, 440, 92, 2.6, 0.4, 2, 32, c["verm"], 0.8)
    b += f'<text x="60" y="116" font-size="13" font-style="italic" fill="{c["mute"]}">Software Engineering · Systems · AI · Mathematics</text>'
    b += seal(c, 780, 78, 40, cj("码", "SC"), 33)
    b += seigaiha(c, 150, 9) + petals(c, 5, (40, 860), 21)
    return wrap(900, 256, c, b)


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
            save(f'card-{proj["id"]}', th, card(c, i, proj, CROPS[i % len(CROPS)]))

    def pic(name, alt, width=None, href=None):
        w = f' width="{width}"' if width else ""
        p = (
            f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
            f'  <img alt="{html.escape(alt)}" src="assets/{name}-light.svg"{w}>\n</picture>'
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
    print("[Japanese Ink Scroll] Generated 3x2 live portfolio assets & README.md")


if __name__ == "__main__":
    main()
