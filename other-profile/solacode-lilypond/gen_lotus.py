#!/usr/bin/env python3
"""
Lily Pond (Monet Impressionism) — High-Craft Project Cards & Section Generator
Reads central shared data from ../../profile-data.json and painting crops from ../../src/crops.json.
Pure Python (zero external font dependencies) while preserving the Monet Impressionist palette & art.
"""
import html
import json
import math
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent if (HERE.parent.name == "other-profile") else HERE
ASSETS = HERE / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

DATA = json.loads((ROOT / "profile-data.json").read_text(encoding="utf-8"))
CROPS = json.loads((ROOT / "src" / "crops.json").read_text(encoding="utf-8"))

SERIF = "'Palatino Linotype','Book Antiqua','Iowan Old Style',Georgia,serif"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Consolas,Menlo,monospace"

TH = {
    "dark": dict(
        bg="#0a1f26",
        bg2="#07161b",
        text="#f3f1cf",
        muted="#a8c2b6",
        acc="#cfd94f",
        acc2="#5fb4a2",
        live="#5de6a4",
        line="#2f6a62",
        fire="#ffd95a",
        tilebg="#0e2a31",
        tilebg2="#12363e",
        pillbg="#092128",
        halo="#06191e",
    ),
    "light": dict(
        bg="#f5f4e1",
        bg2="#ecebd2",
        text="#12322c",
        muted="#47665c",
        acc="#2f6f4f",
        acc2="#267382",
        live="#178556",
        line="#9bb8a2",
        fire="#d9a21b",
        tilebg="#fbfaec",
        tilebg2="#f1f0dc",
        pillbg="#edf1e1",
        halo="#0a2a30",
    ),
}

CROP_ORDER = ["yellow", "blue", "spiral", "drops", "field", "pond"]


def esc(s):
    return html.escape(str(s), quote=False)


def pl(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def pad(cx, cy, R, notch=-125, nw=8, sc=0.028, k=9):
    a0, a1 = math.radians(notch + nw / 2), math.radians(notch + 360 - nw / 2)
    pts = [
        (
            cx + R * (1 + sc * math.sin(k * a)) * math.cos(a),
            cy + R * (1 + sc * math.sin(k * a)) * math.sin(a),
        )
        for a in (a0 + (a1 - a0) * i / 120 for i in range(121))
    ]
    return f"M{cx:.1f},{cy:.1f} L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


def padicon(cx, cy, r, fill, hi, vein):
    v = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx + 0.86 * r * math.cos(math.radians(a)):.1f}" '
        f'y2="{cy + 0.86 * r * math.sin(math.radians(a)):.1f}" stroke="{vein}" stroke-width="1" opacity=".55"/>'
        for a in range(-30, 300, 36)
    )
    return (
        f'<path d="{pad(cx, cy, r, sc=0.04, k=7)}" fill="{fill}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.42:.1f}" fill="{hi}" opacity=".5"/>{v}'
    )


def img(name, x, y, w, h, extra=""):
    b = CROPS[name]["b64"]
    return (
        f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'href="data:image/jpeg;base64,{b}" xlink:href="data:image/jpeg;base64,{b}" '
        f'preserveAspectRatio="xMidYMid slice" {extra}/>'
    )


def svg(W, H, body, label, defs="", style=""):
    st = f"<style>{style}</style>" if style else ""
    out = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">'
        f"<defs>{defs}</defs>{st}{body}</svg>"
    )
    return re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", out)


def wrap_words(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def overlay(kind, cx, cy, r, c):
    ink, halo = "#fffbd6", c["halo"]
    paths = []
    dots = ""

    if kind == "leetresume":
        # LaTeX sheet + DeepSeek AI neural constellation rays
        paths.append(f"M{cx-26:.1f},{cy-34:.1f} h52 v68 h-52 Z")
        for j in range(4):
            w = 34 if j != 2 else 24
            paths.append(f"M{cx-17:.1f},{cy-18+j*12:.1f} h{w}")
        for ang in (-35, 10, 55, 145, 205):
            a = math.radians(ang)
            ex, ey = cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)
            paths.append(f"M{cx+26*math.cos(a):.1f},{cy+26*math.sin(a):.1f} L{ex:.1f},{ey:.1f}")
            dots += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.4" fill="{ink}"/>'
        dots += (
            f'<circle cx="{cx+24:.1f}" cy="{cy-26:.1f}" r="5.5" fill="{c["fire"]}">'
            f'<animate attributeName="opacity" values=".5;1;.5" dur="3.6s" repeatCount="indefinite"/></circle>'
        )

    elif kind == "fastdl":
        # High-speed stream waves + transfer chevron + flying packet
        for dy, amp in ((-24, 7), (0, 9), (24, 7)):
            pts = [(cx - r + i * (2 * r / 24), cy + dy + amp * math.sin(i * 0.55)) for i in range(25)]
            paths.append(pl(pts))
        paths.append(f"M{cx:.1f},{cy-32:.1f} V{cy+24:.1f} M{cx-18:.1f},{cy+6:.1f} L{cx:.1f},{cy+24:.1f} L{cx+18:.1f},{cy+6:.1f}")
        track = f"M{cx-r:.1f},{cy:.1f} Q{cx:.1f},{cy-20:.1f} {cx+r:.1f},{cy:.1f}"
        dots = f'<circle r="4.5" fill="{c["fire"]}"><animateMotion dur="5s" repeatCount="indefinite" path="{track}"/></circle>'

    elif kind == "lazy-equation":
        # Twin Archimedean spiral + orbiting planet
        for a in range(2):
            paths.append(
                pl(
                    [
                        (
                            cx + r * 1.02 * t * math.cos(t * 2.8 * 2 * math.pi + a * math.pi),
                            cy + r * 1.02 * t * math.sin(t * 2.8 * 2 * math.pi + a * math.pi),
                        )
                        for t in (i / 100 for i in range(101))
                    ]
                )
            )
        orbit = f"M{cx - r*1.15:.1f},{cy:.1f} a{r*1.15:.1f},{r*0.42:.1f} 0 1 0 {r*2.3:.1f},0 a{r*1.15:.1f},{r*0.42:.1f} 0 1 0 {-r*2.3:.1f},0"
        paths.append(orbit)
        dots = f'<circle r="4.6" fill="{c["fire"]}"><animateMotion dur="12s" repeatCount="indefinite" path="{orbit}"/></circle>'

    elif kind == "xstudio":
        # Layered precision PDF pages + 9-tool modular corners
        paths.append(f"M{cx-30:.1f},{cy-34:.1f} h46 l14,14 v54 h-60 Z")
        paths.append(f"M{cx+16:.1f},{cy-34:.1f} v14 h14")
        paths.append(f"M{cx-40:.1f},{cy-22:.1f} h10 M{cx-40:.1f},{cy-22:.1f} v60 h52")
        for j in range(3):
            paths.append(f"M{cx-18:.1f},{cy-6+j*12:.1f} h34")
        dots = (
            f'<circle cx="{cx+20:.1f}" cy="{cy-20:.1f}" r="4.2" fill="{c["fire"]}"/>'
            f'<circle cx="{cx-28:.1f}" cy="{cy+26:.1f}" r="3.2" fill="{ink}"/>'
        )

    elif kind == "md-converter":
        # Document streams converging into clean Markdown "#" structure
        paths.append(f"M{cx-r*0.95:.1f},{cy-22:.1f} C{cx-10:.1f},{cy-22:.1f} {cx-16:.1f},{cy:.1f} {cx+8:.1f},{cy:.1f}")
        paths.append(f"M{cx-r*0.95:.1f},{cy+22:.1f} C{cx-10:.1f},{cy+22:.1f} {cx-16:.1f},{cy:.1f} {cx+8:.1f},{cy:.1f}")
        paths.append(f"M{cx-r*0.95:.1f},{cy:.1f} H{cx+8:.1f}")
        # Crisp Markdown '#' glyph on right
        hx = cx + 24
        paths.append(f"M{hx-6:.1f},{cy-22:.1f} L{hx-12:.1f},{cy+22:.1f} M{hx+10:.1f},{cy-22:.1f} L{hx+4:.1f},{cy+22:.1f}")
        paths.append(f"M{hx-18:.1f},{cy-8:.1f} H{hx+18:.1f} M{hx-20:.1f},{cy+8:.1f} H{hx+16:.1f}")
        flow = f"M{cx-r*0.95:.1f},{cy:.1f} H{cx+10:.1f}"
        dots = f'<circle r="4.2" fill="{c["fire"]}"><animateMotion dur="4.5s" repeatCount="indefinite" path="{flow}"/></circle>'

    else:  # chemify
        # Hexagonal benzene ring + inclined Bohr atomic orbitals + orbiting electron
        hex_pts = [(cx + r * 0.56 * math.cos(math.radians(a)), cy + r * 0.56 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        paths.append(pl(hex_pts + [hex_pts[0]]))
        for rot in (0, 60, -60):
            rad = math.radians(rot)
            pts = []
            for i in range(49):
                t = 2 * math.pi * i / 48
                ex, ey = r * 1.02 * math.cos(t), r * 0.38 * math.sin(t)
                rx = ex * math.cos(rad) - ey * math.sin(rad)
                ry = ex * math.sin(rad) + ey * math.cos(rad)
                pts.append((cx + rx, cy + ry))
            paths.append(pl(pts))
        orbit = f"M{cx - r*1.02:.1f},{cy:.1f} a{r*1.02:.1f},{r*0.38:.1f} 0 1 0 {r*2.04:.1f},0 a{r*1.02:.1f},{r*0.38:.1f} 0 1 0 {-r*2.04:.1f},0"
        dots = (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.2" fill="{c["fire"]}"/>'
            f'<circle r="3.8" fill="{ink}"><animateMotion dur="7s" repeatCount="indefinite" path="{orbit}"/></circle>'
        )

    out = "".join(
        f'<path d="{d}" fill="none" stroke="{halo}" stroke-opacity=".5" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>'
        for d in paths
    ) + "".join(
        f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        for d in paths
    )
    return f"<g>{out}{dots}</g>"


def projects_title(m):
    c = TH[m]
    W, H = 1200, 110
    cx, cy, r = 56, 55, 38
    box = CROPS["field"]
    D = 2 * r * 1.25
    x0 = 490
    pts = [(x, 54 + 5 * math.sin((x - x0) / 58)) for x in range(x0, 995, 12)]
    p_str = pl(pts)
    defs = f'<clipPath id="c3"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
    body = (
        img("field", cx - D / 2, cy - D / 2 * box["h"] / box["w"], D, D * box["h"] / box["w"], 'clip-path="url(#c3)"')
        + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c["acc"]}" stroke-width="2.2"/>'
        + f'<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="none" stroke="{c["acc2"]}" stroke-width="1" stroke-dasharray="2 6" opacity=".8"/>'
        + f'<text x="116" y="59" font-family="{SERIF}" font-size="42" font-weight="700" fill="{c["text"]}">Selected Projects</text>'
        + f'<text x="116" y="88" font-family="{SERIF}" font-size="20" font-style="italic" fill="{c["muted"]}">six live deployed products</text>'
        + f'<path d="{p_str}" fill="none" stroke="{c["line"]}" stroke-width="1.4"/>'
        + f'<circle r="2.8" fill="{c["fire"]}"><animateMotion dur="12s" repeatCount="indefinite" path="{p_str}"/></circle>'
        + f'<rect x="1010" y="36" width="144" height="34" rx="17" fill="{c["tilebg"]}" stroke="{c["acc2"]}" stroke-opacity=".75"/>'
        + f'<circle cx="1031" cy="53" r="4.5" fill="{c["live"]}"><animate attributeName="opacity" values="1;.35;1" dur="2.4s" repeatCount="indefinite"/></circle>'
        + f'<text x="1044" y="57.5" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing="1.2" fill="{c["text"]}">6 LIVE APPS</text>'
        + padicon(1176, 54, 13, "#b1ba42", "#e0e283", c["bg"])
    )
    return svg(W, H, body, "Selected Projects — six live deployed products", defs)


def card(m, idx, proj):
    c = TH[m]
    W, H = 580, 272
    cx, cy, r = 112, 136, 82
    crop = CROP_ORDER[idx % len(CROP_ORDER)]
    box = CROPS[crop]
    D = 2 * r * 1.24
    hh = D * box["h"] / box["w"]
    cid = f"k{idx}"

    defs = (
        f'<linearGradient id="cg{idx}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c["tilebg"]}"/><stop offset="1" stop-color="{c["tilebg2"]}"/></linearGradient>'
        f'<radialGradient id="gl{idx}" cx=".2" cy=".5" r=".55">'
        f'<stop offset="0" stop-color="{c["acc2"]}" stop-opacity=".18"/><stop offset="1" stop-color="{c["acc2"]}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
    )

    body = [
        f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="16" fill="url(#cg{idx})" stroke="{c["acc"]}" stroke-opacity=".42" stroke-width="1.3"/>',
        f'<rect x="6" y="6" width="{W-12}" height="{H-12}" rx="12" fill="url(#gl{idx})" stroke="{c["acc2"]}" stroke-opacity=".16" stroke-width=".9"/>',
        # Corner ripples
        f'<path d="M{W-56},{H-12} a44,44 0 0 1 44,-44" fill="none" stroke="{c["acc2"]}" stroke-opacity=".45"/>',
        f'<path d="M{W-36},{H-12} a24,24 0 0 1 24,-24" fill="none" stroke="{c["acc2"]}" stroke-opacity=".32"/>',
        # Circular Monet medallion
        img(crop, cx - D / 2, cy - hh / 2, D, hh, f'clip-path="url(#{cid})"'),
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c["acc"]}" stroke-width="2.2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="{c["acc2"]}" stroke-width="1.1" stroke-dasharray="2 6" opacity=".82"/>',
        f'<g clip-path="url(#{cid})">{overlay(proj["id"], cx, cy, r * 0.78, c)}</g>',
    ]

    x = 224
    # Top row: number + LIVE pill badge
    badge_txt = proj.get("badge", "Live").upper()
    body.append(
        f'<text x="{x}" y="60" font-family="{SERIF}" font-size="38" font-style="italic" font-weight="700" fill="{c["acc"]}">{esc(proj["number"])}</text>'
    )
    pill_w = len(badge_txt) * 7.2 + 56
    px = W - 24 - pill_w
    body.append(
        f'<rect x="{px:.1f}" y="28" width="{pill_w:.1f}" height="24" rx="12" fill="{c["pillbg"]}" stroke="{c["live"]}" stroke-opacity=".65"/>'
        f'<circle cx="{px+14:.1f}" cy="40" r="3.6" fill="{c["live"]}"><animate attributeName="opacity" values="1;.3;1" dur="2.6s" repeatCount="indefinite"/></circle>'
        f'<text x="{px+24:.1f}" y="43.8" font-family="{MONO}" font-size="10" font-weight="700" letter-spacing=".8" fill="{c["text"]}">LIVE · {esc(badge_txt)}</text>'
    )

    # Title
    body.append(
        f'<text x="{x}" y="102" font-family="{SERIF}" font-size="30" font-weight="700" fill="{c["text"]}">{esc(proj["title"])}</text>'
    )

    # Description (clean 2 lines)
    desc_lines = wrap_words(proj["description"], 40)[:2]
    for j, ln in enumerate(desc_lines):
        body.append(
            f'<text x="{x}" y="{134 + j * 23}" font-family="{SERIF}" font-size="16.5" font-style="italic" fill="{c["muted"]}">{esc(ln)}</text>'
        )

    # Tech stack pills (max 4, safely inside card width)
    tx = x
    for tag in proj["tags"][:4]:
        tw = len(tag) * 7.2 + 20
        if tx + tw > W - 20:
            break
        body.append(
            f'<rect x="{tx:.1f}" y="182" width="{tw:.1f}" height="25" rx="12.5" fill="{c["pillbg"]}" stroke="{c["acc2"]}" stroke-opacity=".75"/>'
            f'<text x="{tx + tw/2:.1f}" y="198.5" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="600" fill="{c["text"]}">{esc(tag)}</text>'
        )
        tx += tw + 8

    # Divider hairline & live domain footer
    body.append(f'<line x1="{x}" y1="224" x2="{W-24}" y2="224" stroke="{c["line"]}" stroke-opacity=".55"/>')
    body.append(
        f'<text x="{x}" y="247" font-family="{MONO}" font-size="12" font-weight="600" fill="{c["acc2"]}">{esc(proj["display_url"])}</text>'
        f'<text x="{W-26}" y="247" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="700" fill="{c["acc"]}">OPEN LIVE ↗</text>'
    )

    return svg(
        W,
        H,
        "".join(body),
        f'Project {proj["number"]}: {proj["title"]}. {proj["description"]} Tags: {", ".join(proj["tags"])}.',
        defs,
    )


def write_readme():
    links = DATA["links"]
    about = DATA["profile"]["about"]
    projects = DATA["projects"]

    def card_td(p):
        slug = p["id"]
        alt = html.escape(f'Project {p["number"]}, {p["title"]}: {p["description"]}')
        return (
            f'<td width="50%"><a href="{p["live_url"]}">'
            f'<picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="./assets/card-{slug}-dark.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="./assets/card-{slug}-light.svg">'
            f'<img alt="{alt}" src="./assets/card-{slug}-dark.svg" width="100%">'
            f'</picture></a></td>'
        )

    rows = []
    for i in range(0, len(projects), 2):
        pair = projects[i : i + 2]
        rows.append("<tr>\n" + "\n".join(card_td(p) for p in pair) + "\n</tr>")

    readme = f"""<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/header-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/header-light.svg"><img alt="Solayman El Mouden, Software Engineer. AI, Math, Newest Technologies. Lily-pond painting with a frog on a pad." src="./assets/header-dark.svg" width="100%"></picture>

<a href="{links['github']}"><img src="https://img.shields.io/badge/GitHub-solacode--SC?style=for-the-badge&logo=github&logoColor=white&labelColor=12322c&color=2f6f4f" alt="GitHub"></a>
<a href="{links['linkedin']}"><img src="https://img.shields.io/badge/LinkedIn-Solayman_El_Mouden?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=12322c&color=2d7f8f" alt="LinkedIn"></a>
<a href="{links['portfolio']}"><img src="https://img.shields.io/badge/Portfolio-{links['portfolio_display']}?style=for-the-badge&logo=safari&logoColor=white&labelColor=12322c&color=6a934f" alt="Portfolio"></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/divider-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/divider-light.svg"><img alt="" src="./assets/divider-dark.svg" width="100%"></picture>

</div>

<div align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/about-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/about-light.svg"><img alt="About" src="./assets/about-dark.svg" width="100%"></picture></div>

{about[0]}

{about[1]}

<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/approach-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/approach-light.svg"><img alt="" src="./assets/approach-dark.svg" width="100%"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/divider-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/divider-light.svg"><img alt="" src="./assets/divider-dark.svg" width="100%"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/skills-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/skills-light.svg"><img alt="Technologies" src="./assets/skills-dark.svg" width="100%"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/skills-grid-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/skills-grid-light.svg"><img alt="" src="./assets/skills-grid-dark.svg" width="100%"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/divider-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/divider-light.svg"><img alt="" src="./assets/divider-dark.svg" width="100%"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/projects-title-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/projects-title-light.svg"><img alt="Selected Projects — 6 live deployed apps" src="./assets/projects-title-dark.svg" width="100%"></picture>

</div>

<table>
{chr(10).join(rows)}
</table>

<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/footer-dark.svg"><source media="(prefers-color-scheme: light)" srcset="./assets/footer-light.svg"><img alt="Build, Explore, Understand. Software Engineering, Systems, AI, Mathematics." src="./assets/footer-dark.svg" width="100%"></picture>

[{links['portfolio_display']}]({links['portfolio']}) · [LinkedIn]({links['linkedin']}) · [GitHub]({links['github']})

</div>
"""
    (HERE / "README.md").write_text(readme, encoding="utf-8")


def main():
    # Clean old card SVGs
    for old in ASSETS.glob("card-*.svg"):
        old.unlink()

    for m in TH:
        (ASSETS / f"projects-title-{m}.svg").write_text(projects_title(m), encoding="utf-8")
        for i, proj in enumerate(DATA["projects"]):
            (ASSETS / f'card-{proj["id"]}-{m}.svg').write_text(card(m, i, proj), encoding="utf-8")

    write_readme()
    print(f"[Lily Pond] Generated 6 live project cards & title (dark+light) and README.md")


if __name__ == "__main__":
    main()
