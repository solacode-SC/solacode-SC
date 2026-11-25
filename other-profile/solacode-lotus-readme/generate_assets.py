#!/usr/bin/env python3
"""
Kintsugi Lotus Pond — Enhanced 3x2 Live Portfolio Edition.
Reads central data from ../../profile-data.json.
Generates animated light/dark SVG assets and README.md.
"""
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

ROOT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ROOT_DIR.parent.parent
ASSETS = ROOT_DIR / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
SRC = Image.open(ROOT_DIR / "art" / "source.jpg").convert("RGB")
DATA = json.loads((REPO_ROOT / "profile-data.json").read_text(encoding="utf-8"))

NAME_1, NAME_2 = DATA["profile"]["first_name"], DATA["profile"]["last_name"]
HANDLE = DATA["profile"]["handle"]
GITHUB = DATA["links"]["github"]
PORTFOLIO = DATA["links"]["portfolio"]
PORTFOLIO_DISPLAY = DATA["links"]["portfolio_display"]
LINKEDIN = DATA["links"]["linkedin"]
ROLE = "SOFTWARE ENGINEER"
PILLARS = "AI  |  Math  |  Newest Technologies"
TAGLINE = DATA["profile"]["tagline_lines"]
ABOUT = [
    "I'm Solayman El Mouden, a software engineer",
    "focused on systems, web technologies,",
    "artificial intelligence and mathematics.",
    "I enjoy understanding how things work underneath",
    "the abstraction and turning that knowledge into",
    "useful software.",
]
JOURNEY = [
    ("C / C++", "Systems"),
    ("Python", "Backend & AI"),
    ("TypeScript", "Web & Tools"),
    ("Docker", "Infrastructure"),
    ("Linux", "DevOps"),
]
SKILLS = [(s["name"], s["short"]) for s in DATA["skills"]]
PROJECTS = DATA["projects"]
# 6 crop centers (cx, cy, width) on art/source.jpg (736x1313)
PROJECT_CROPS = [
    (350, 340, 320),
    (220, 650, 380),
    (520, 140, 260),
    (270, 930, 300),
    (480, 830, 340),
    (480, 1130, 300),
]

FOOT_1 = "Build  \u00b7  Explore  \u00b7  Understand"
FOOT_2 = "Software Engineering \u00b7 Systems \u00b7 AI \u00b7 Mathematics"
BRAND = "NashirTech  \u00b7  \u0646\u0627\u0634\u0631 \u062a\u0643"
HERO_CROP = (30, 530, 630, 1290)
AVATAR_CROP = (270, 260, 430, 420)

SERIF = "Georgia,'Iowan Old Style','Palatino Linotype','DejaVu Serif',serif"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Consolas,Menlo,monospace"

THEMES = {
    "dark": dict(
        bg="#06151b",
        panel="#0d2a34",
        panel2="#103440",
        ink="#e8f2ef",
        mut="#9dbdbb",
        teal="#1d7f8f",
        teal2="#2fa3a8",
        aqua="#69cbc6",
        live="#5de6a4",
        leaf1="#155f73",
        leaf2="#0c3f55",
        gold="#e2bb63",
        goldtx="#e2bb63",
        koi="#ea5a2c",
        koi2="#b83a18",
        paper="#efdcb8",
        seal="#d6402a",
        sealtxt="#fbeed6",
        chip="#12404d",
        strip="#e9d6b0",
    ),
    "light": dict(
        bg="#f1e3c6",
        panel="#fbf4e1",
        panel2="#f3e8cc",
        ink="#13303a",
        mut="#465f65",
        teal="#14707f",
        teal2="#1e8d95",
        aqua="#2f9aa0",
        live="#168052",
        leaf1="#1c7c8a",
        leaf2="#0f5566",
        gold="#a2711f",
        goldtx="#7d5510",
        koi="#d2461c",
        koi2="#a8300f",
        paper="#fffaf0",
        seal="#c23520",
        sealtxt="#fff4e0",
        chip="#e6d7b4",
        strip="#2a1f10",
    ),
}

CSS = """.a{transform-box:fill-box;transform-origin:center}
.sway{animation:sway 9s ease-in-out infinite alternate}
@keyframes sway{from{transform:rotate(-3deg)}to{transform:rotate(3deg)}}
.swim{animation:swim 15s ease-in-out infinite alternate}
@keyframes swim{from{transform:translate(0,0)}to{transform:translate(40px,-5px)}}
.rip{opacity:.3;animation:rip 8s ease-out infinite}
@keyframes rip{0%{transform:scale(.2);opacity:.7}100%{transform:scale(1.5);opacity:0}}
.kb{animation:kb 24s ease-in-out infinite alternate}
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.07)}}
.dash{animation:dash 7s linear infinite}
@keyframes dash{to{stroke-dashoffset:-60}}
.shim{animation:shim 9s ease-in-out infinite}
@keyframes shim{0%,55%{transform:translateX(-120px)}100%{transform:translateX(420px)}}
.pulse{animation:pl 2.6s ease-in-out infinite}
@keyframes pl{0%,100%{opacity:1}50%{opacity:.3}}
@media (prefers-reduced-motion: reduce){.sway,.swim,.rip,.kb,.dash,.shim,.pulse{animation:none}}"""


def esc(s):
    return html.escape(str(s), quote=False)


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def uri(cx_cy_w=None, box=None, size=(520, 200), q=82):
    W_img, H_img = SRC.size
    if box is None:
        cx, cy, w = cx_cy_w
        h = w * size[1] / size[0]
        x0 = max(0, min(W_img - w, cx - w / 2))
        y0 = max(0, min(H_img - h, cy - h / 2))
        box = (x0, y0, x0 + w, y0 + h)
    box = tuple(int(round(b)) for b in box)
    im = SRC.crop(box).resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def save(name, theme, svg_text):
    svg_text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)", "&amp;", svg_text)
    (ASSETS / f"{name}-{theme}.svg").write_text(svg_text, encoding="utf-8")


def root(w, h, T, title, body, extra_defs=""):
    d = (
        f"<defs>"
        f'<radialGradient id="lg" cx=".4" cy=".38" r=".8"><stop offset="0" stop-color="{T["teal2"]}"/>'
        f'<stop offset=".55" stop-color="{T["leaf1"]}"/><stop offset="1" stop-color="{T["leaf2"]}"/></radialGradient>'
        f'<linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["panel"]}"/>'
        f'<stop offset="1" stop-color="{T["panel2"]}"/></linearGradient>'
        f'<linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#041014" stop-opacity=".12"/>'
        f'<stop offset="1" stop-color="#041014" stop-opacity=".55"/></linearGradient>'
        f'<linearGradient id="pt" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{T["paper"]}"/>'
        f'<stop offset=".6" stop-color="{T["paper"]}"/><stop offset="1" stop-color="{T["aqua"]}"/></linearGradient>'
        f'<linearGradient id="shg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["gold"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{T["gold"]}" stop-opacity=".38"/><stop offset="1" stop-color="{T["gold"]}" stop-opacity="0"/></linearGradient>'
        f'<filter id="noise" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/>'
        f'<feColorMatrix values="0 0 0 0 .5  0 0 0 0 .4  0 0 0 0 .3  0 0 0 .55 -.18"/></filter>'
        f"{extra_defs}</defs>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title><style>{CSS}</style>{d}{body}"
        f'<rect class="grain" width="{w}" height="{h}" fill="#000" opacity=".45" filter="url(#noise)"/></svg>'
    )


def leaf(r, T, seed, n=14, wav=0.05):
    rng = random.Random(seed)
    ph = rng.random() * 6.28
    pts = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        rr = r * (1 + wav * math.sin(3 * a + ph) + wav * 0.6 * math.sin(7 * a + ph * 2))
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + "Z"
    veins = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.05, 0.05)
        ex, ey = r * 0.94 * math.cos(a), r * 0.94 * math.sin(a)
        cx, cy = r * 0.5 * math.cos(a + 0.12), r * 0.5 * math.sin(a + 0.12)
        veins.append(f"M0,0Q{f(cx)},{f(cy)} {f(ex)},{f(ey)}")
        if r > 20:
            mx, my = r * 0.6 * math.cos(a + 0.08), r * 0.6 * math.sin(a + 0.08)
            for s in (-0.3, 0.3):
                veins.append(f"M{f(mx)},{f(my)}L{f(r*.9*math.cos(a+s*.5))},{f(r*.9*math.sin(a+s*.5))}")
    g = T["gold"]
    return (
        f'<path d="{d}" fill="url(#lg)" stroke="{g}" stroke-width="1" stroke-opacity=".8"/>'
        f'<path d="{" ".join(veins)}" fill="none" stroke="{g}" stroke-width=".8" stroke-opacity=".85" stroke-linecap="round"/>'
        f'<circle r="{f(r*.55)}" fill="none" stroke="{g}" stroke-width=".6" stroke-dasharray="1 4" opacity=".5"/>'
        f'<circle r="{f(max(r*.05, 1.5))}" fill="{g}"/>'
    )


def place(x, y, inner, delay=0, cls="sway", scale=1, op=None):
    o = f' opacity="{op}"' if op is not None else ""
    return (
        f'<g transform="translate({f(x)},{f(y)}) scale({scale})"{o}>'
        f'<g class="a {cls}" style="animation-delay:{delay}s">{inner}</g></g>'
    )


def koi(T, x, y, s=1.0, flip=False, delay=0, patch=True):
    sx = -s if flip else s
    koi_c, k2, g = T["koi"], T["koi2"], T["gold"]
    p = f'<path d="M26,-9C40,-13 60,-9 66,-5C56,-2 40,-4 26,-9Z" fill="{T["paper"]}" opacity=".85"/>' if patch else ""
    return (
        f'<g transform="translate({f(x)},{f(y)}) scale({f(sx)},{f(s)})"><g class="a swim" style="animation-delay:{delay}s">'
        f'<path d="M0,0C8,-9 30,-13 55,-9C75,-6 90,-2 104,0L126,-13C121,-5 119,-1 119,2C119,5 121,9 126,16L104,4C90,7 75,10 55,9C30,12 8,8 0,0Z" '
        f'fill="{koi_c}" stroke="{g}" stroke-width=".9" stroke-linejoin="round"/>{p}'
        f'<path d="M32,5C35,15 44,21 54,23C49,14 44,9 40,6Z" fill="{k2}" stroke="{g}" stroke-width=".6"/>'
        f'<path d="M42,-10C52,-18 68,-18 80,-8Z" fill="{k2}" stroke="{g}" stroke-width=".6"/>'
        f'<path d="M70,-6q6,6 0,13M80,-5q6,5 0,11M90,-3q5,4 0,8" fill="none" stroke="{g}" stroke-width=".6" opacity=".75"/>'
        f'<circle cx="9" cy="-2" r="1.6" fill="{T["bg"]}"/></g></g>'
    )


def lotus(T, x, y, s=1.0):
    pet = "M0,0C-12,-14 -11,-30 0,-38C11,-30 12,-14 0,0Z"
    st, out = T["teal"], []
    for a in (-64, -40, -16, 16, 40, 64):
        out.append(f'<path d="{pet}" transform="rotate({a})" fill="url(#pt)" stroke="{st}" stroke-width=".8" opacity=".9"/>')
    for a in (-50, -26, 0, 26, 50):
        out.append(f'<path d="{pet}" transform="rotate({a}) scale(.88)" fill="url(#pt)" stroke="{st}" stroke-width=".8"/>')
    out.append(f'<circle cy="-4" r="3" fill="{T["gold"]}"/>')
    return f'<g transform="translate({f(x)},{f(y)}) scale({s})">{"".join(out)}</g>'


def seal(T, x, y, txt, size=24, rot=-3, fs=None):
    fs = fs or size * 0.5
    return (
        f'<g transform="translate({f(x)},{f(y)}) rotate({rot})"><rect width="{size}" height="{f(size*.8)}" rx="3" fill="{T["seal"]}"/>'
        f'<rect x="2" y="2" width="{size-4}" height="{f(size*.8-4)}" rx="2" fill="none" stroke="{T["sealtxt"]}" stroke-width=".7" opacity=".6"/>'
        f'<text x="{f(size/2)}" y="{f(size*.8/2+fs*.35)}" text-anchor="middle" font-family="{MONO}" font-size="{f(fs)}" '
        f'font-weight="700" fill="{T["sealtxt"]}">{txt}</text></g>'
    )


def strip(x, y, w, h, T, rng, op):
    d = " ".join(f"M{x+4},{yy}H{x+w-4}" for yy in range(y + 6, y + h - 4, 9))
    pat = " ".join(str(rng.choice([1, 2, 3, 5, 7])) for _ in range(6))
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{T["strip"]}" opacity="{op}"/>'
        f'<path d="{d}" stroke="{T["ink"]}" stroke-width="1.6" stroke-dasharray="{pat}" opacity="{f(op*1.6)}" fill="none"/>'
    )


def divider(T, x0, x1, y, delay=0):
    pts = " L".join(f"{x},{f(y + 2.2*math.sin(x/38))}" for x in range(int(x0), int(x1) + 1, 10))
    g = T["gold"]
    nodes = "".join(f'<circle cx="{x}" cy="{f(y + 2.2*math.sin(x/38))}" r="2.2" fill="{g}"/>' for x in range(int(x0) + 70, int(x1), 160))
    return (
        f'<path d="M{pts}" fill="none" stroke="{g}" stroke-width="1" opacity=".7"/>'
        f'<path d="M{pts}" fill="none" stroke="{T["paper"]}" stroke-width="2" stroke-linecap="round" '
        f'stroke-dasharray="1 14" class="dash" style="animation-delay:{delay}s" opacity=".8"/>{nodes}'
    )


def label(T, x, y, num, text):
    return (
        f'{seal(T, x, y-17, num, 24, -3, 11)}'
        f'<text x="{x+34}" y="{y}" font-family="{MONO}" font-size="12.5" letter-spacing="3" fill="{T["goldtx"]}" font-weight="700">{text}</text>'
    )


def ripples(T, cx, cy, rx, delay=0):
    return "".join(
        f'<ellipse class="a rip" cx="{cx}" cy="{cy}" rx="{rx}" ry="{f(rx*.28)}" fill="none" stroke="{T["teal2"]}" '
        f'stroke-width="1.2" style="animation-delay:{delay - i*2.6}s"/>'
        for i in range(3)
    )


def hero(T, th):
    rng = random.Random(11)
    img = uri(box=HERO_CROP, size=(600, 760), q=80)
    av = uri(box=AVATAR_CROP, size=(64, 64), q=80)
    b = [
        f'<rect width="900" height="500" fill="{T["bg"]}"/>',
        '<clipPath id="pc"><rect width="900" height="500"/></clipPath>',
        '<g clip-path="url(#pc)">',
    ]
    for x, w, op in [(472, 30, 0.10), (512, 48, 0.13), (640, 60, 0.12), (840, 60, 0.14)]:
        b.append(strip(x, 0, w, 500, T, rng, op))
    b.append(place(850, 40, leaf(120, T, 3, 20), 0, op=0.7))
    b.append(place(520, 540, leaf(130, T, 5, 20), -4, op=0.7))
    b.append(ripples(T, 140, 470, 120, 0))
    b.append("</g>")
    b.append(
        '<clipPath id="hc"><rect x="564" y="68" width="284" height="364" rx="4"/></clipPath>'
        f'<linearGradient id="vg" x1="0" y1="0" x2="0" y2="1"><stop offset=".6" stop-color="{T["bg"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{T["bg"]}" stop-opacity=".55"/></linearGradient>'
    )
    b.append(f'<rect x="556" y="60" width="300" height="380" rx="7" fill="{T["panel"]}" stroke="{T["gold"]}" stroke-width="1.6"/>')
    b.append(
        f'<g clip-path="url(#hc)"><image class="a kb" x="564" y="68" width="284" height="364" preserveAspectRatio="xMidYMid slice" xlink:href="{img}"/>'
        f'<rect x="564" y="68" width="284" height="364" fill="url(#vg)"/>'
        f'<g transform="skewX(-20)"><rect class="a shim" x="560" y="68" width="40" height="364" fill="url(#shg)"/></g></g>'
    )
    b.append(f'<rect x="564" y="68" width="284" height="364" rx="4" fill="none" stroke="{T["gold"]}" stroke-width=".8" opacity=".8"/>')
    b.append(seal(T, 826, 46, "SC", 34, 5, 14))
    b.append(
        '<clipPath id="av"><circle cx="76" cy="52" r="14"/></clipPath>'
        f'<image x="62" y="38" width="28" height="28" clip-path="url(#av)" xlink:href="{av}"/>'
        f'<circle cx="76" cy="52" r="14" fill="none" stroke="{T["gold"]}" stroke-width="1.2"/>'
        f'<text x="100" y="56" font-family="{MONO}" font-size="12.5" fill="{T["mut"]}">{HANDLE} / README</text>'
        f'<path d="M62,78H500" stroke="{T["gold"]}" stroke-width=".8" stroke-dasharray="2 5" opacity=".7"/>'
    )
    b.append(
        f'<text x="62" y="136" font-family="{SERIF}" font-style="italic" font-size="22" fill="{T["mut"]}">Hi, I\'m</text>'
        f'<text x="60" y="204" font-family="{SERIF}" font-weight="700" font-size="66" fill="{T["ink"]}">{esc(NAME_1)}</text>'
        f'<text x="60" y="272" font-family="{SERIF}" font-weight="700" font-size="66" fill="{T["ink"]}">{esc(NAME_2)}</text>'
        f'<text x="62" y="312" font-family="{MONO}" font-weight="700" font-size="14" letter-spacing="5" fill="{T["goldtx"]}">{ROLE}</text>'
        f'<text x="62" y="338" font-family="{MONO}" font-size="13" fill="{T["ink"]}">{PILLARS}</text>'
    )
    for i, ln in enumerate(TAGLINE):
        b.append(f'<text x="62" y="{380 + i*22}" font-family="{SERIF}" font-size="15" fill="{T["mut"]}">{esc(ln)}</text>')
    b.append(koi(T, 70, 466, 0.9, delay=0) + koi(T, 330, 482, 0.6, True, -6, False))
    return root(900, 500, T, f"{NAME_1} {NAME_2} - {ROLE.title()}", "".join(b))


def button(T, th, text):
    g = T["gold"]
    b = (
        f'<rect x="1" y="1" width="148" height="38" rx="19" fill="{T["panel"]}" stroke="{g}" stroke-width="1.4"/>'
        + place(22, 20, leaf(10, T, 7, 8), 0)
        + f'<text x="42" y="25" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing="1.8" fill="{T["ink"]}">{text}</text>'
    )
    return root(150, 40, T, text.title(), b)


def about(T, th):
    rng = random.Random(21)
    b = [
        f'<rect width="900" height="310" fill="{T["bg"]}"/>',
        '<clipPath id="pc"><rect width="900" height="310"/></clipPath><g clip-path="url(#pc)">',
        strip(0, 0, 36, 310, T, rng, 0.10),
        strip(864, 0, 36, 310, T, rng, 0.10),
        place(905, 365, leaf(100, T, 9, 18), -2, op=0.55),
        "</g>",
        label(T, 56, 52, "01", "ABOUT"),
        label(T, 540, 52, "02", "MY JOURNEY"),
    ]
    for i, ln in enumerate(ABOUT):
        b.append(f'<text x="58" y="{104 + i*28}" font-family="{SERIF}" font-size="15" fill="{T["ink"]}">{esc(ln)}</text>')
    for i, (lang, area) in enumerate(JOURNEY):
        y = 106 + i * 38
        b.append(
            place(534, y - 5, leaf(7, T, 20 + i, 8), -i, scale=1)
            + f'<text x="550" y="{y}" font-family="{MONO}" font-size="14" font-weight="700" fill="{T["ink"]}">{lang}</text>'
            + f'<path d="M652,{y-5}H704" stroke="{T["gold"]}" stroke-width="1.4" stroke-linecap="round" stroke-dasharray="1 7" class="dash" style="animation-delay:-{i}s"/>'
            + f'<text x="716" y="{y}" font-family="{SERIF}" font-size="15" fill="{T["ink"]}">{area}</text>'
        )
    b.append(divider(T, 56, 844, 292))
    b.append(koi(T, 60, 276, 0.55, delay=-3))
    return root(900, 310, T, "About Solayman El Mouden and his journey", "".join(b))


def skills(T, th):
    b = [
        f'<rect width="900" height="340" fill="{T["bg"]}"/>',
        label(T, 56, 52, "03", "TECHNOLOGIES &amp; SKILLS"),
        divider(T, 56, 844, 76, -2),
    ]
    for i, (name, mono) in enumerate(SKILLS):
        cx = 121.5 + (i % 6) * 131
        cy = 134 + (i // 6) * 112
        inner = (
            leaf(38, T, 40 + i, 12)
            + f'<circle r="17" fill="{T["leaf2"]}" stroke="{T["gold"]}" stroke-width="1"/>'
            + f'<text y="5" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="700" fill="{T["sealtxt"]}">{esc(mono)}</text>'
        )
        b.append(place(cx, cy, inner, -i * 0.7))
        b.append(f'<text x="{f(cx)}" y="{cy + 60}" text-anchor="middle" font-family="{SERIF}" font-size="12.5" fill="{T["ink"]}">{esc(name)}</text>')
    return root(900, 340, T, "Technologies and skills: " + ", ".join(s[0] for s in SKILLS), "".join(b))


def projects_title(T, th):
    b = (
        f'<rect width="900" height="84" fill="{T["bg"]}"/>'
        + label(T, 56, 44, "04", "SELECTED LIVE PROJECTS")
        + koi(T, 540, 40, 0.65, delay=-2)
        + f'<rect x="706" y="25" width="138" height="26" rx="13" fill="{T["panel"]}" stroke="{T["gold"]}" stroke-width="1.1"/>'
        + f'<circle class="pulse" cx="723" cy="38" r="3.4" fill="{T["live"]}"/>'
        + f'<text x="734" y="42" font-family="{MONO}" font-size="10" font-weight="700" letter-spacing="1" fill="{T["ink"]}">6 DEPLOYED APPS</text>'
        + divider(T, 56, 844, 70, -3)
    )
    return root(900, 84, T, "Selected live projects", b)


def chips(T, tags):
    out, x, y = [], 14, 180
    for t in tags:
        w = len(t) * 6.3 + 16
        if x + w > 274:
            break
        out.append(
            f'<rect x="{f(x)}" y="{y}" width="{f(w)}" height="20" rx="10" fill="{T["chip"]}" stroke="{T["gold"]}" stroke-width=".7" stroke-opacity=".75"/>'
            f'<text x="{f(x+w/2)}" y="{y+13.5}" text-anchor="middle" font-family="{MONO}" font-size="9.5" font-weight="600" fill="{T["ink"]}">{esc(t)}</text>'
        )
        x += w + 6
    return "".join(out)


def card(T, th, i, proj):
    W, H = 288, 250
    img = uri(PROJECT_CROPS[i % len(PROJECT_CROPS)], size=(530, 200), q=82)
    d1, d2 = proj["description_lines"][:2]
    tags = proj.get("card_tags", proj["tags"][:3])
    b = [
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#cbg)" stroke="{T["gold"]}" stroke-width="1.3"/>',
        f'<rect x="5" y="5" width="{W-10}" height="{H-10}" rx="9" fill="none" stroke="{T["gold"]}" stroke-opacity=".22" stroke-width=".8"/>',
        f'<clipPath id="tc{i}"><rect x="10" y="10" width="268" height="98" rx="7"/></clipPath>',
        f'<g clip-path="url(#tc{i})">'
        f'<image class="a kb" x="10" y="10" width="268" height="98" preserveAspectRatio="xMidYMid slice" xlink:href="{img}" style="animation-delay:-{i*3}s"/>'
        f'<rect x="10" y="10" width="268" height="98" fill="url(#scrim)"/>'
        f'<g transform="skewX(-20)"><rect class="a shim" x="20" y="10" width="32" height="98" fill="url(#shg)" style="animation-delay:-{i*1.3}s"/></g></g>',
        f'<rect x="10" y="10" width="268" height="98" rx="7" fill="none" stroke="{T["gold"]}" stroke-width=".9" opacity=".85"/>',
        seal(T, 18, 18, proj["number"], 28, -3, 11),
        # Top-right LIVE badge
        f'<rect x="212" y="18" width="58" height="20" rx="10" fill="#06151b" fill-opacity=".82" stroke="{T["live"]}" stroke-opacity=".8"/>',
        f'<circle class="pulse" cx="224" cy="28" r="3" fill="{T["live"]}"/>',
        f'<text x="233" y="31.5" font-family="{MONO}" font-size="9" font-weight="700" letter-spacing=".8" fill="#e8f2ef">LIVE</text>',
        # Title & description
        f'<text x="14" y="135" font-family="{SERIF}" font-weight="700" font-size="17.5" fill="{T["ink"]}">{esc(proj["title"])}</text>',
        f'<text x="14" y="155" font-family="{SERIF}" font-size="12" fill="{T["mut"]}">{esc(d1)}</text>',
        f'<text x="14" y="170" font-family="{SERIF}" font-size="12" fill="{T["mut"]}">{esc(d2)}</text>',
        chips(T, tags),
        f'<line x1="14" y1="213" x2="{W-14}" y2="213" stroke="{T["gold"]}" stroke-opacity=".35"/>',
        f'<text x="14" y="233" font-family="{MONO}" font-size="9.5" fill="{T["mut"]}">{esc(proj["display_url"])}</text>',
        f'<text x="{W-14}" y="233" text-anchor="end" font-family="{MONO}" font-size="9.8" font-weight="700" fill="{T["goldtx"]}">OPEN ↗</text>',
    ]
    return root(W, H, T, f'{proj["title"]} — {proj["description"]}', "".join(b))


def footer(T, th):
    b = [
        f'<rect width="900" height="250" fill="{T["bg"]}"/>',
        '<clipPath id="pc"><rect width="900" height="250"/></clipPath><g clip-path="url(#pc)">',
        ripples(T, 450, 228, 210, 0),
        place(40, 270, leaf(140, T, 61, 20), 0, op=0.8),
        place(870, 280, leaf(150, T, 62, 22), -3, op=0.8),
        f'<path d="M165,250V215M735,250V210" stroke="{T["teal"]}" stroke-width="2"/>',
        lotus(T, 165, 215, 1.1),
        lotus(T, 735, 210, 1.2),
        koi(T, 330, 205, 1.0, delay=0),
        koi(T, 640, 232, 0.75, True, -5),
        "</g>",
        f'<text x="450" y="80" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="30" fill="{T["ink"]}">{FOOT_1}</text>',
        f'<text x="450" y="110" text-anchor="middle" font-family="{MONO}" font-size="12.5" letter-spacing="1" fill="{T["mut"]}">{FOOT_2}</text>',
        divider(T, 230, 670, 136, -1),
        f'<text x="450" y="162" text-anchor="middle" font-family="{SERIF}" font-size="13" fill="{T["goldtx"]}">{BRAND}</text>',
    ]
    return root(900, 250, T, "Footer: Build, Explore, Understand", "".join(b))


def pic(name, alt, width="100%", href=None):
    h = (
        f'<picture>\n    <source media="(prefers-color-scheme: dark)"  srcset="assets/{name}-dark.svg">\n'
        f'    <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
        f'    <img alt="{html.escape(alt)}" src="assets/{name}-light.svg" width="{width}">\n  </picture>'
    )
    return f'<a href="{href}">\n  {h}\n</a>' if href else f"  {h}"


def write_readme():
    cards = [
        pic(f'card-{p["id"]}', f'{p["title"]}: {p["description"]}', "32%", p["live_url"]) for p in PROJECTS
    ]
    L = [
        '<div align="center">',
        "",
        pic("hero", f"{NAME_1} {NAME_2}, software engineer. AI, Math, Newest Technologies. Lotus pond and koi artwork."),
        "",
        " &nbsp; ".join(
            [
                pic("btn-github", "GitHub profile", "150", GITHUB),
                pic("btn-linkedin", "LinkedIn profile", "150", LINKEDIN),
                pic("btn-portfolio", "Portfolio website", "150", PORTFOLIO),
            ]
        ),
        "",
        pic("about", "About Solayman El Mouden and his journey: C/C++ systems, Python backend and AI, TypeScript web and tools, Docker infrastructure, Linux DevOps."),
        "",
        pic("skills", "Technologies and skills: " + ", ".join(s[0] for s in SKILLS) + "."),
        "",
        pic("projects-title", "Selected live projects"),
        "",
        "\n".join(cards[:3]),
        "",
        "\n".join(cards[3:6]),
        "",
        pic("footer", "Build, Explore, Understand. Software Engineering, Systems, AI, Mathematics."),
        "",
        f'<sub><a href="{PORTFOLIO}">{PORTFOLIO_DISPLAY}</a> &nbsp;·&nbsp; <a href="{LINKEDIN}">LinkedIn</a> &nbsp;·&nbsp; <a href="{GITHUB}">GitHub</a></sub>',
        "",
        "</div>",
        "",
    ]
    (ROOT_DIR / "README.md").write_text("\n".join(L), encoding="utf-8")


def main():
    for old in ASSETS.glob("card-*.svg"):
        old.unlink()

    for th, T in THEMES.items():
        save("hero", th, hero(T, th))
        for n, t in (("github", "GITHUB"), ("linkedin", "LINKEDIN"), ("portfolio", "PORTFOLIO")):
            save(f"btn-{n}", th, button(T, th, t))
        save("about", th, about(T, th))
        save("skills", th, skills(T, th))
        save("projects-title", th, projects_title(T, th))
        for i, p in enumerate(PROJECTS):
            save(f'card-{p["id"]}', th, card(T, th, i, p))
        save("footer", th, footer(T, th))
    write_readme()
    print("[Kintsugi Lotus Pond] Generated 3x2 live portfolio assets & README.md")


if __name__ == "__main__":
    main()
