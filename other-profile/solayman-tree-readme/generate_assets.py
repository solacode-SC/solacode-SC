#!/usr/bin/env python3
"""
Topographic Tree — Enhanced 2x3 Clickable Live Projects Edition.
Reads central data from ../../profile-data.json and tree artwork crops from art/crops.json.
Generates dark & light projects-title + 6 individual clickable project cards (586x210)
and updates README.md with a crisp 2x3 interactive live showcase.
"""
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
ASSETS = HERE / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

DATA = json.loads((REPO_ROOT / "profile-data.json").read_text(encoding="utf-8"))
CROPS = json.loads((HERE / "art" / "crops.json").read_text(encoding="utf-8"))
CROP_KEYS = ["knot", "full", "roots", "canopy", "cloud_branch", "hero_trunk"]

THEMES = {
    "dark": dict(
        bg1="#09111c",
        bg2="#0e1a2b",
        card1="#132338",
        card2="#0f1c2e",
        border="rgba(86, 207, 225, 0.28)",
        border_soft="rgba(86, 207, 225, 0.14)",
        cyan="#56cfe1",
        mint="#72efdd",
        gold="#e0a96d",
        title="#f2f7fc",
        body="#a2bad2",
        pill_bg="#16273e",
        pill_stroke="#284b6e",
        pill_txt="#b9d4ec",
        live_bg="#0b1f29",
    ),
    "light": dict(
        bg1="#f5f8fc",
        bg2="#ebf2fa",
        card1="#ffffff",
        card2="#f6faff",
        border="rgba(35, 110, 165, 0.28)",
        border_soft="rgba(35, 110, 165, 0.14)",
        cyan="#1b6ca8",
        mint="#0077b6",
        gold="#b37428",
        title="#0e1c2b",
        body="#425970",
        pill_bg="#edf4fc",
        pill_stroke="#bdd5ec",
        pill_txt="#1e496e",
        live_bg="#e8f5fa",
    ),
}

STYLE = """
.font-sans { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, sans-serif; }
.font-serif { font-family: "Cinzel", "Playfair Display", Georgia, serif; }
.font-mono { font-family: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, monospace; }
.pulse { animation: pulse 2.6s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
@media (prefers-reduced-motion: reduce) { .pulse { animation: none !important; } }
"""


def esc(s):
    return html.escape(str(s), quote=False)


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


def get_crop_b64(key):
    val = CROPS[key]
    if isinstance(val, dict):
        return val.get("b64") or val.get("data") or next(iter(val.values()))
    return val


def contour_arcs(cx, cy, col):
    out = []
    for r, op in ((34, 0.25), (56, 0.18), (78, 0.12)):
        pts = []
        for i in range(25):
            a = math.pi + i * (math.pi / 2) / 24
            rr = r * (1 + 0.06 * math.sin(5 * a))
            pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
        out.append(f'<path d="M{" L".join(pts)}" fill="none" stroke="{col}" stroke-width="1" stroke-dasharray="4 4" opacity="{op}"/>')
    return "".join(out)


def projects_title(T):
    W, H = 1200, 96
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Selected Live Projects">
    <defs>
        <linearGradient id="ptBg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="{T['bg1']}"/>
            <stop offset="100%" stop-color="{T['bg2']}"/>
        </linearGradient>
    </defs>
    <style>{STYLE}</style>
    <rect width="{W}" height="{H}" rx="16" fill="url(#ptBg)"/>
    <rect width="{W}" height="{H}" rx="16" fill="none" stroke="{T['border']}" stroke-width="1.2"/>
    <g transform="translate(48, 38)">
        <text x="0" y="0" fill="{T['gold']}" font-size="11.5" font-weight="700" letter-spacing="1.8" class="font-mono">DEPLOYED PRODUCTION SYSTEMS</text>
        <text x="0" y="28" fill="{T['title']}" font-size="24" font-weight="700" class="font-serif">Selected Live Projects</text>
        <line x1="330" y1="18" x2="950" y2="18" stroke="{T['border_soft']}" stroke-width="1.2"/>
        <g transform="translate(966, 2)">
            <rect width="144" height="30" rx="15" fill="{T['live_bg']}" stroke="{T['cyan']}" stroke-opacity=".6"/>
            <circle cx="18" cy="15" r="4.2" fill="{T['mint']}" class="pulse"/>
            <text x="31" y="19" fill="{T['title']}" font-size="11" font-weight="700" letter-spacing="1" class="font-mono">6 LIVE APPS</text>
        </g>
    </g>
</svg>"""


def card(T, idx, proj):
    W, H = 588, 214
    crop_key = CROP_KEYS[idx % len(CROP_KEYS)]
    b64 = get_crop_b64(crop_key)
    if not b64.startswith("data:"):
        b64 = "data:image/jpeg;base64," + b64
    desc_lines = wrap_words(proj["description"], 76)[:2]
    subtitle = proj.get("subtitle", proj["badge"])
    badge = proj.get("badge", "Live").upper()

    pills = []
    px = 0.0
    for tag in proj["tags"][:4]:
        pw = len(tag) * 6.8 + 18
        if px + pw > 350:
            break
        pills.append(
            f'<g transform="translate({px:.1f}, 0)">'
            f'<rect width="{pw:.1f}" height="22" rx="6" fill="{T["pill_bg"]}" stroke="{T["pill_stroke"]}" stroke-width="0.9"/>'
            f'<text x="{pw/2:.1f}" y="14.5" text-anchor="middle" fill="{T["pill_txt"]}" font-size="9.8" font-weight="600" class="font-mono">{esc(tag)}</text>'
            f"</g>"
        )
        px += pw + 7

    pill_w = len(badge) * 6.8 + 52
    bx = W - 20 - pill_w

    svg_text = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(proj['title'])} — {esc(proj['description'])}">
    <defs>
        <linearGradient id="cBg{idx}" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="{T['card1']}"/>
            <stop offset="100%" stop-color="{T['card2']}"/>
        </linearGradient>
        <clipPath id="pc{idx}">
            <rect width="62" height="62" rx="9" x="2" y="2"/>
        </clipPath>
    </defs>
    <style>{STYLE}</style>
    <rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="15" fill="url(#cBg{idx})" stroke="{T['border']}" stroke-width="1.3"/>
    {contour_arcs(W, H, T['cyan'])}

    <!-- Left Art Emblem -->
    <g transform="translate(20, 20)">
        <rect width="66" height="66" rx="11" fill="none" stroke="{T['gold']}" stroke-width="1.4"/>
        <g clip-path="url(#pc{idx})">
            <image x="2" y="2" width="62" height="62" preserveAspectRatio="xMidYMid slice" href="{b64}" xlink:href="{b64}"/>
        </g>
        <rect x="2" y="2" width="62" height="62" rx="9" fill="none" stroke="{T['border']}" stroke-width="1"/>
    </g>

    <!-- Header -->
    <text x="102" y="38" fill="{T['cyan']}" font-size="11" font-weight="700" letter-spacing="1.2" class="font-mono">PROJECT #{esc(proj['number'])}</text>
    <text x="102" y="62" fill="{T['title']}" font-size="20" font-weight="700" class="font-sans">{esc(proj['title'])}</text>
    <text x="102" y="81" fill="{T['gold']}" font-size="11.5" font-weight="600" class="font-sans">{esc(subtitle)}</text>

    <!-- Top Right LIVE Pill -->
    <g transform="translate({bx:.1f}, 20)">
        <rect width="{pill_w:.1f}" height="24" rx="12" fill="{T['live_bg']}" stroke="{T['mint']}" stroke-opacity=".65"/>
        <circle cx="13" cy="12" r="3.6" fill="{T['mint']}" class="pulse"/>
        <text x="23" y="15.8" fill="{T['title']}" font-size="9.5" font-weight="700" letter-spacing=".8" class="font-mono">LIVE · {esc(badge)}</text>
    </g>

    <!-- Description (properly word-wrapped) -->
    <text x="20" y="114" fill="{T['body']}" font-size="12" class="font-sans">
        <tspan x="20" dy="0">{esc(desc_lines[0])}</tspan>
        <tspan x="20" dy="18">{esc(desc_lines[1] if len(desc_lines) > 1 else '')}</tspan>
    </text>

    <!-- Bottom divider -->
    <line x1="20" y1="148" x2="{W-20}" y2="148" stroke="{T['border_soft']}" stroke-width="1"/>

    <!-- Tech Stack Pills & Live URL -->
    <g transform="translate(20, 160)">
        {"".join(pills)}
    </g>
    <text x="{W-20}" y="175" text-anchor="end" fill="{T['cyan']}" font-size="10.5" font-weight="700" class="font-mono">OPEN LIVE ↗</text>
    <text x="20" y="200" fill="{T['gold']}" font-size="10.2" font-weight="600" class="font-mono">{esc(proj['display_url'])}</text>
</svg>"""
    return re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", svg_text)


def write_readme():
    links = DATA["links"]
    projects = DATA["projects"]

    def card_td(p):
        slug = p["id"]
        alt = html.escape(f'Project #{p["number"]} {p["title"]} — {p["description"]}')
        return (
            f'  <td width="50%"><a href="{p["live_url"]}">'
            f'<picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/card-{slug}-dark.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="assets/card-{slug}-light.svg">'
            f'<img alt="{alt}" src="assets/card-{slug}-dark.svg" width="100%">'
            f'</picture></a></td>'
        )

    rows = []
    for i in range(0, len(projects), 2):
        rows.append("<tr>\n" + "\n".join(card_td(p) for p in projects[i : i + 2]) + "\n</tr>")

    quick_links = " &nbsp;•&nbsp;\n  ".join(
        f'<a href="{p["live_url"]}"><b>[ {p["number"]} · {p["title"]} ↗ ]</b></a>' for p in projects
    )

    readme = f"""<div align="center">

<!-- HERO BANNER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/header-light.svg">
  <img alt="Solayman El Mouden — Software Engineer" src="assets/header-dark.svg" width="100%">
</picture>

<br>

<!-- CONNECT BUTTONS -->
<p align="center">
  <a href="{links['github']}">
    <img src="https://img.shields.io/badge/GitHub-solacode--SC-132338?style=for-the-badge&logo=github&logoColor=56cfe1&labelColor=09111c" alt="GitHub">
  </a>
  &nbsp;
  <a href="{links['linkedin']}">
    <img src="https://img.shields.io/badge/LinkedIn-Solayman_El_Mouden-132338?style=for-the-badge&logo=linkedin&logoColor=e0a96d&labelColor=09111c" alt="LinkedIn">
  </a>
  &nbsp;
  <a href="{links['portfolio']}">
    <img src="https://img.shields.io/badge/Portfolio-{links['portfolio_display']}-132338?style=for-the-badge&logo=safari&logoColor=72efdd&labelColor=09111c" alt="Portfolio">
  </a>
</p>

<!-- SECTION DIVIDER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/divider-light.svg">
  <img alt="Contour Divider" src="assets/divider-dark.svg" width="100%">
</picture>

<br>

<!-- FOUR PILLARS / ABOUT -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/about-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/about-light.svg">
  <img alt="Architectural Methodology and Pillars" src="assets/about-dark.svg" width="100%">
</picture>

<br><br>

<!-- GROWTH RINGS / SKILLS MATRIX -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/skills-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/skills-light.svg">
  <img alt="Annular Growth Rings and Technical Stack" src="assets/skills-dark.svg" width="100%">
</picture>

<br><br>

<!-- SECTION DIVIDER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/divider-light.svg">
  <img alt="Contour Divider" src="assets/divider-dark.svg" width="100%">
</picture>

<br>

<!-- SELECTED LIVE PROJECTS HEADER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/projects-title-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/projects-title-light.svg">
  <img alt="Selected Live Projects" src="assets/projects-title-dark.svg" width="100%">
</picture>

</div>

<table>
{chr(10).join(rows)}
</table>

<div align="center">

<!-- QUICK LIVE LAUNCH BAR -->
<p align="center">
  {quick_links}
</p>

<br>

<!-- FOOTER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/footer-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/footer-light.svg">
  <img alt="Build, Explore, Understand" src="assets/footer-dark.svg" width="100%">
</picture>

<br>

<sub>Designed with organic topographic algorithms · <a href="{links['portfolio']}">{links['portfolio_display']}</a> · <a href="{links['linkedin']}">LinkedIn</a></sub>

</div>
"""
    (HERE / "README.md").write_text(readme, encoding="utf-8")


def main():
    # Clean legacy projects-grid and old cards
    for old in list(ASSETS.glob("card-*.svg")) + list(ASSETS.glob("projects-grid-*.svg")):
        old.unlink()

    for th, T in THEMES.items():
        (ASSETS / f"projects-title-{th}.svg").write_text(projects_title(T), encoding="utf-8")
        for i, proj in enumerate(DATA["projects"]):
            (ASSETS / f'card-{proj["id"]}-{th}.svg').write_text(card(T, i, proj), encoding="utf-8")

    write_readme()
    print("[Topographic Tree] Generated 2x3 clickable live project cards & README.md")


if __name__ == "__main__":
    main()
