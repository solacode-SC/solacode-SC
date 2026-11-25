#!/usr/bin/env python3
"""Autumn-garden edition — Enhanced 3x2 Live Portfolio Edition.
Reads central data from ../../profile-data.json and crops art/source.jpg into
hero poster + micro vignettes, layering CSS-animated SVG (falling leaves, glowing eyes,
lantern flicker, swaying twigs) with high-craft live project cards."""
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

MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Consolas,Menlo,monospace"
SERIF = "Georgia,'Iowan Old Style','Palatino Linotype','DejaVu Serif',serif"

THEMES = {
    "dark": dict(
        bg1="#17120d",
        bg2="#0d0a07",
        fg="#f4ebd6",
        mute="#c2b08f",
        acc="#f28f3b",
        acc2="#e8c46a",
        live="#6de39b",
        line="#3d2f21",
        card="#1e1710",
        card2="#251d14",
        pill="#140f0a",
        ink="#120e0b",
        leaves=["#e0782f", "#c8262e", "#8f9d3d", "#d9a441"],
    ),
    "light": dict(
        bg1="#f6eedc",
        bg2="#eadfc5",
        fg="#241a14",
        mute="#66523f",
        acc="#c4561a",
        acc2="#8a6a1a",
        live="#1a854b",
        line="#cdbb9a",
        card="#fbf5e6",
        card2="#f4ead4",
        pill="#efe3ca",
        ink="#120e0b",
        leaves=["#d4691f", "#b3262c", "#7f8d33", "#c9942f"],
    ),
}

NAME = DATA["profile"]["name"]
GITHUB = DATA["links"]["github"]
LINKEDIN = DATA["links"]["linkedin"]
PORTFOLIO = DATA["links"]["portfolio"]
PORTFOLIO_DISPLAY = DATA["links"]["portfolio_display"]
CREDIT = "Artwork by Crimson-Chains"

JOURNEY = [
    ("C / C++", "Systems"),
    ("Python", "Backend & AI"),
    ("TypeScript", "Web & Tools"),
    ("Docker", "Infrastructure"),
    ("Linux", "DevOps"),
]
SKILLS = [(s["name"], s["short"]) for s in DATA["skills"]]

# 6 balanced high-contrast crops in art/source.jpg (736x1128) — aspect ~268x86
CROPS = [
    (95, 420, 365, 510),
    (350, 435, 620, 525),
    (92, 185, 362, 275),
    (200, 600, 470, 690),
    (430, 585, 700, 675),
    (300, 775, 570, 865),
]
PROJECTS = DATA["projects"]


def esc(s):
    return html.escape(str(s), quote=False)


def crop64(box, size, q=82):
    im = ART.crop(box).resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


STYLE = """<style>
.fall{animation:fall linear infinite}
@keyframes fall{from{transform:translateY(-40px)}to{transform:translateY(520px)}}
.sway{transform-box:fill-box;transform-origin:center;animation:sway ease-in-out infinite alternate}
@keyframes sway{from{transform:translateX(-20px) rotate(-38deg)}to{transform:translateX(20px) rotate(38deg)}}
.leafsway{transform-box:fill-box;transform-origin:50% 100%;animation:ls 6s ease-in-out infinite alternate}
@keyframes ls{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}
.glow{animation:glow 6s ease-in-out infinite}
@keyframes glow{0%,100%{opacity:.2}50%{opacity:.85}}
.lid{opacity:0;animation:blink 7.5s linear infinite}
@keyframes blink{0%,93%,100%{opacity:0}94.5%,97%{opacity:1}}
.breathe{transform-box:fill-box;transform-origin:center;animation:br 26s ease-in-out infinite alternate}
@keyframes br{from{transform:scale(1)}to{transform:scale(1.06)}}
.flick{animation:fl 2.6s ease-in-out infinite}
@keyframes fl{0%,100%{opacity:.75}30%{opacity:1}55%{opacity:.6}80%{opacity:.95}}
.pulse{animation:pl 2.4s ease-in-out infinite}
@keyframes pl{0%,100%{opacity:1}50%{opacity:.35}}
.cursor{animation:cur 1.1s steps(1) infinite}
@keyframes cur{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){.fall,.sway,.leafsway,.glow,.lid,.breathe,.flick,.pulse,.cursor{animation:none}}
</style>"""


def f1(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


LEAF = "M0 -11C9 -8 11 5 0 13C-11 5 -9 -8 0 -11Z"


def leaf(x, y, s, col, rot=0, rib="#000"):
    return (
        f'<g transform="translate({f1(x)} {f1(y)}) rotate({f1(rot)}) scale({f1(s)})"><path d="{LEAF}" fill="{col}"/>'
        f'<path d="M0 -8V11" stroke="{rib}" stroke-opacity=".3" stroke-width="1"/></g>'
    )


def falling(c, n, xr, seed=3):
    r = random.Random(seed)
    o = []
    for _ in range(n):
        x = r.uniform(*xr)
        s = r.uniform(0.65, 1.25)
        col = r.choice(c["leaves"])
        d = r.uniform(15, 26)
        dl = -r.uniform(0, d)
        sd = r.uniform(3.5, 6.5)
        o.append(
            f'<g transform="translate({f1(x)} 0)"><g class="fall" style="animation-duration:{d:.1f}s;animation-delay:{dl:.1f}s">'
            f'<g class="sway" style="animation-duration:{sd:.1f}s;animation-delay:{-r.uniform(0, sd):.1f}s">'
            f'{leaf(0, 0, s, col, r.uniform(0, 180))}</g></g></g>'
        )
    return "".join(o)


def twig(x, y, ang, ln, depth, r, out):
    if depth == 0 or ln < 5:
        return
    x2, y2 = x + ln * math.cos(ang), y + ln * math.sin(ang)
    out.append(f"M{f1(x)} {f1(y)}L{f1(x2)} {f1(y2)}")
    for da in (-0.45, 0.4):
        if r.random() < 0.85:
            twig(x2, y2, ang + da + r.uniform(-0.12, 0.12), ln * r.uniform(0.62, 0.78), depth - 1, r, out)


def twigs(c, specs, seed=2):
    r = random.Random(seed)
    o = []
    for x, y, ang, ln, d in specs:
        twig(x, y, math.radians(ang), ln, d, r, o)
    return f'<path d="{"".join(o)}" fill="none" stroke="{c["mute"]}" stroke-opacity=".38" stroke-width="1.2" stroke-linecap="round"/>'


def defs(c):
    return f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c['bg1']}"/><stop offset="1" stop-color="{c['bg2']}"/></linearGradient>
<linearGradient id="cardbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c['card']}"/><stop offset="1" stop-color="{c['card2']}"/></linearGradient>
<linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0a07" stop-opacity=".18"/><stop offset="1" stop-color="#0d0a07" stop-opacity=".68"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".35" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="warm"><stop offset="0" stop-color="#ffb347" stop-opacity=".85"/><stop offset=".5" stop-color="#f28f3b" stop-opacity=".3"/><stop offset="1" stop-color="#f28f3b" stop-opacity="0"/></radialGradient>
</defs>"""


def wrap(w, h, c, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{MONO}">'
        f'{STYLE}{defs(c)}<rect width="{w}" height="{h}" fill="url(#bg)"/>{body}'
        f'<path d="M.5 0V{h}M{w-.5} 0V{h}" stroke="{c["line"]}"/></svg>'
    )


def divider(c, y, w=900, seed=1):
    r = random.Random(seed)
    pts = [(x, y + 2.5 * math.sin(x / 45)) for x in range(40, w - 39, 6)]
    d = "M" + "L".join(f"{f1(a)} {f1(b)}" for a, b in pts)
    o = [f'<path d="{d}" fill="none" stroke="{c["line"]}" stroke-width="1.4"/>']
    for i, x in enumerate(range(80, w - 60, 78)):
        yy = y + 2.5 * math.sin(x / 45)
        up = i % 2 == 0
        o.append(
            f'<g class="leafsway" style="animation-delay:{-r.uniform(0, 6):.1f}s">'
            f'{leaf(x, yy + (-9 if up else 9), 0.55, c["leaves"][i % 4], -25 if up else 155, c["ink"])}</g>'
        )
    return "".join(o)


def heading(c, y, idx, label, x=60):
    return (
        leaf(x, y, 0.85, c["acc"], 35, c["ink"])
        + f'<text x="{x+22}" y="{y+4}" font-size="12" letter-spacing="2" fill="{c["mute"]}">{idx} /</text>'
        + f'<text x="{x+62}" y="{y+4}" font-size="12" font-weight="700" letter-spacing="2" fill="{c["fg"]}">{label}</text>'
    )


EYES = [(577, 147), (616, 128)]


def hero(c):
    px, py, pw, ph = 486, 48, 384, 365
    img = crop64((0, 60, 736, 759), (700, 665), 80)
    b = twigs(c, [(0, 0, 38, 70, 5), (410, 0, 100, 55, 4), (-4, 410, -30, 60, 4)])
    b += (
        f'<defs><clipPath id="pc"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14"/></clipPath></defs>'
        f'<g clip-path="url(#pc)"><g class="breathe"><image x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid slice" href="{img}" xlink:href="{img}"/></g>'
    )
    for ex, ey in EYES:
        b += (
            f'<ellipse class="lid" cx="{ex}" cy="{ey}" rx="13" ry="16" fill="#14100f"/>'
            f'<circle class="glow" cx="{ex}" cy="{ey}" r="34" fill="url(#halo)"/>'
        )
    b += (
        f'</g><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="none" stroke="{c["acc"]}" stroke-width="1.6"/>'
        f'<rect x="{px-7}" y="{py-7}" width="{pw+14}" height="{ph+14}" rx="19" fill="none" stroke="{c["line"]}" stroke-dasharray="2 5"/>'
    )
    av = crop64((255, 615, 345, 705), (64, 64), 82)
    b += (
        f'<defs><clipPath id="av"><circle cx="72" cy="34" r="13"/></clipPath></defs>'
        f'<image x="59" y="21" width="26" height="26" clip-path="url(#av)" href="{av}" xlink:href="{av}"/>'
        f'<circle cx="72" cy="34" r="13" fill="none" stroke="{c["acc"]}" stroke-width="1.4"/>'
        f'<text x="94" y="38" font-size="12" fill="{c["mute"]}">solacode-SC <tspan fill="{c["line"]}">/</tspan> README</text>'
    )
    b += (
        f'<text x="60" y="118" font-size="13" letter-spacing="3" fill="{c["mute"]}">HI, I\'M</text>'
        f'<text x="58" y="168" font-size="38" font-family="{SERIF}" font-style="italic" fill="{c["fg"]}">{esc(NAME)}</text>'
        f'<text x="60" y="212" font-size="16" font-weight="700" letter-spacing="3" fill="{c["acc"]}">SOFTWARE ENGINEER</text>'
        f'<rect class="cursor" x="308" y="198" width="9" height="16" fill="{c["acc"]}"/>'
        f'<text x="60" y="254" font-size="13" letter-spacing="1" fill="{c["fg"]}" xml:space="preserve">AI  ·  Math  ·  Newest Technologies</text>'
        f'<rect x="60" y="270" width="36" height="2" fill="{c["acc"]}"/>'
    )
    for i, t in enumerate(["Building systems, web applications,", "developer tools and intelligent software", "for a better tomorrow."]):
        b += f'<text x="60" y="{302+i*20}" font-size="12.5" fill="{c["mute"]}">{t}</text>'
    b += divider(c, 430, seed=4) + falling(c, 15, (330, 880), seed=7)
    return wrap(900, 445, c, b)


def button(c, label):
    w = 156
    b = (
        f'<rect x=".75" y=".75" width="{w-1.5}" height="38.5" rx="19" fill="{c["card"]}" stroke="{c["acc"]}" stroke-opacity=".85" stroke-width="1.3"/>'
        + leaf(26, 20, 0.8, c["acc"], 40, c["ink"])
        + f'<text x="45" y="24.5" font-size="11.5" font-weight="700" letter-spacing="1.4" fill="{c["fg"]}">{label.upper()}</text>'
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 40" width="{w}" height="40" font-family="{MONO}">{b}</svg>'


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
    b += f'<path d="M450 74V246" stroke="{c["line"]}" stroke-dasharray="2 5"/>'
    b += heading(c, 42, "02", "MY JOURNEY", 480)
    for i, (a, t) in enumerate(JOURNEY):
        y = 96 + i * 30
        b += (
            leaf(488, y - 4, 0.62, c["leaves"][i % 4], 30 + i * 25, c["ink"])
            + f'<text x="508" y="{y}" font-size="13" fill="{c["fg"]}">{a}</text>'
            + f'<path d="M640 {y-4}H664M659 {y-8}L664 {y-4}L659 {y}" fill="none" stroke="{c["acc"]}"/>'
            + f'<text x="682" y="{y}" font-size="13" fill="{c["mute"]}">{t}</text>'
        )
    b += divider(c, 274, seed=5)
    return wrap(900, 290, c, b)


def skills(c):
    b = heading(c, 40, "03", "TECHNOLOGIES &amp; SKILLS")
    w, g = 125, 14
    for i, (name, mono) in enumerate(SKILLS):
        x = 40 + (i % 6) * (w + g)
        y = 68 + (i // 6) * 66
        b += (
            f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="53" rx="10" fill="{c["card"]}" stroke="{c["line"]}"/>'
            + leaf(x + w - 14, y + 14, 0.5, c["leaves"][i % 4], 40 + i * 30, c["ink"])
            + f'<text x="{x+w/2}" y="{y+25}" font-size="16" font-weight="700" text-anchor="middle" fill="{c["acc"]}">{esc(mono)}</text>'
            + f'<text x="{x+w/2}" y="{y+43}" font-size="10.5" text-anchor="middle" fill="{c["fg"]}">{esc(name)}</text>'
        )
    b += divider(c, 214, seed=6)
    return wrap(900, 226, c, b)


def projects_title(c):
    b = (
        heading(c, 36, "04", "SELECTED LIVE PROJECTS")
        + f'<rect x="726" y="21" width="134" height="26" rx="13" fill="{c["card"]}" stroke="{c["acc"]}" stroke-opacity=".7"/>'
        + f'<circle class="pulse" cx="743" cy="34" r="3.6" fill="{c["live"]}"/>'
        + f'<text x="754" y="37.8" font-size="10" font-weight="700" letter-spacing="1" fill="{c["fg"]}">6 DEPLOYED APPS</text>'
    )
    return wrap(900, 64, c, b)


def card(c, idx, proj, box):
    w, h = 288, 236
    img = crop64(box, (540, 176), 82)
    d1, d2 = proj["description_lines"][:2]
    tags = proj.get("card_tags", proj["tags"][:3])
    b = (
        f'<defs><clipPath id="cl{idx}"><rect x="10" y="10" width="268" height="86" rx="9"/></clipPath></defs>'
        f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="14" fill="url(#cardbg)" stroke="{c["line"]}" stroke-width="1.4"/>'
        f'<rect x="5" y="5" width="{w-10}" height="{h-10}" rx="10" fill="none" stroke="{c["acc"]}" stroke-opacity=".16"/>'
        f'<g clip-path="url(#cl{idx})">'
        f'<image x="10" y="10" width="268" height="86" preserveAspectRatio="xMidYMid slice" href="{img}" xlink:href="{img}"/>'
        f'<rect x="10" y="10" width="268" height="86" fill="url(#scrim)"/>'
        f"</g>"
        f'<rect x="10" y="10" width="268" height="86" rx="9" fill="none" stroke="{c["acc"]}" stroke-opacity=".75" stroke-width="1.1"/>'
        # Top-left index badge
        f'<rect x="18" y="18" width="32" height="20" rx="10" fill="#120e0b" fill-opacity=".82" stroke="{c["acc2"]}" stroke-opacity=".7"/>'
        f'<text x="34" y="31.5" text-anchor="middle" font-size="9.5" font-weight="700" fill="{c["acc2"]}">{esc(proj["number"])}</text>'
        # Top-right LIVE badge
        f'<rect x="210" y="18" width="58" height="20" rx="10" fill="#120e0b" fill-opacity=".84" stroke="{c["live"]}" stroke-opacity=".75"/>'
        f'<circle class="pulse" cx="222" cy="28" r="3" fill="{c["live"]}"/>'
        f'<text x="231" y="31.5" font-size="9" font-weight="700" letter-spacing=".8" fill="#f4ebd6">LIVE</text>'
        # Decorative autumn leaf corner
        + leaf(258, 86, 0.56, c["leaves"][idx % 4], 30 + idx * 35, c["ink"])
        # Title & description
        + f'<text x="16" y="122" font-size="16" font-weight="700" font-family="{SERIF}" fill="{c["fg"]}">{esc(proj["title"])}</text>'
        + f'<text x="16" y="142" font-size="11" fill="{c["mute"]}">{esc(d1)}</text>'
        + f'<text x="16" y="157" font-size="11" fill="{c["mute"]}">{esc(d2)}</text>'
    )
    x = 16
    for t in tags:
        cw = len(t) * 6.0 + 16
        if x + cw > w - 14:
            break
        b += (
            f'<rect x="{f1(x)}" y="170" width="{f1(cw)}" height="20" rx="10" fill="{c["pill"]}" stroke="{c["line"]}"/>'
            f'<text x="{f1(x+cw/2)}" y="183.5" font-size="9.2" font-weight="600" text-anchor="middle" fill="{c["acc"]}">{esc(t)}</text>'
        )
        x += cw + 6

    # Footer live URL row
    b += (
        f'<line x1="16" y1="204" x2="{w-16}" y2="204" stroke="{c["line"]}" stroke-opacity=".7"/>'
        f'<text x="16" y="222" font-size="9.5" fill="{c["mute"]}">{esc(proj["display_url"])}</text>'
        f'<text x="{w-16}" y="222" text-anchor="end" font-size="10" font-weight="700" fill="{c["acc"]}">OPEN ↗</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{MONO}">{STYLE}{defs(c)}{b}</svg>'
    )


def lantern(c, x, y):
    return (
        f'<circle class="flick" cx="{x}" cy="{y}" r="95" fill="url(#warm)"/>'
        f'<path d="M{x-9} {y-24}a9 9 0 0 1 18 0" fill="none" stroke="{c["mute"]}" stroke-width="1.8"/>'
        f'<rect x="{x-11}" y="{y-20}" width="22" height="5" rx="2" fill="{c["mute"]}"/>'
        f'<rect x="{x-10}" y="{y-15}" width="20" height="26" rx="4" fill="#e0782f" fill-opacity=".9"/>'
        f'<ellipse class="flick" cx="{x}" cy="{y-1}" rx="5" ry="8" fill="#ffe29a"/>'
        f'<rect x="{x-12}" y="{y+10}" width="24" height="5" rx="2" fill="{c["mute"]}"/>'
    )


def footer(c):
    b = ""
    r = random.Random(11)
    for i in range(34):
        x = 20 + i * 26 + r.uniform(-6, 6)
        y = 196 + r.uniform(-6, 10)
        b += (
            f'<g class="leafsway" style="animation-delay:{-r.uniform(0, 6):.1f}s;animation-duration:{r.uniform(5, 8):.1f}s">'
            f'{leaf(x, y, r.uniform(0.8, 1.35), c["leaves"][i % 4], r.uniform(-60, 60), c["ink"])}</g>'
        )
    b = twigs(c, [(60, 0, 80, 60, 5), (840, 0, 100, 55, 5)], seed=9) + b
    b += lantern(c, 450, 150)
    b += (
        f'<text x="450" y="46" font-size="14" font-weight="700" letter-spacing="3" text-anchor="middle" fill="{c["acc"]}" xml:space="preserve">BUILD  ·  EXPLORE  ·  UNDERSTAND</text>'
        f'<text x="450" y="68" font-size="10.5" letter-spacing="1" text-anchor="middle" fill="{c["mute"]}" xml:space="preserve">Software Engineering · Systems · AI · Mathematics</text>'
        f'<text x="450" y="226" font-size="9" text-anchor="middle" fill="{c["mute"]}" opacity=".9">{CREDIT}</text>'
    )
    b += falling(c, 6, (80, 820), seed=21)
    return wrap(900, 236, c, b)


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
    print("[Autumn Garden] Generated 3x2 live portfolio assets & README.md")


if __name__ == "__main__":
    main()
