#!/usr/bin/env python3
"""
Solayman El Mouden (solacode-SC) - Profile README Rotation Engine
================================================================
Automatically rotates GitHub profile README templates on a customizable cycle (e.g., every 12 hours).
Powered by a single shared data file: profile-data.json

Commands:
    python rotate.py --next             Advance to next theme in the collection
    python rotate.py --theme <name>     Switch directly to a specified theme
    python rotate.py --status           Display active theme, schedule, and collection status
    python rotate.py --list             List all available themes
    python rotate.py --sync             Sync all templates with profile-data.json links & texts
    python rotate.py --interval <hours> Update rotation interval (updates workflow cron too)
    python rotate.py --verify           Verify all themes, assets, and dark/light mode integrity
"""

import os
import sys
import json
import shutil
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "profile-data.json"
THEMES_DIR = ROOT_DIR / "other-profile"
ASSETS_DIR = ROOT_DIR / "assets"
README_FILE = ROOT_DIR / "README.md"
WORKFLOW_FILE = ROOT_DIR / ".github" / "workflows" / "rotate-readme.yml"


def load_data():
    """Load and validate the shared profile-data.json file."""
    if not DATA_FILE.exists():
        sys.exit(f"Error: Shared data file not found at {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    """Save the updated shared profile-data.json file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_available_themes():
    """Discover all themes inside other-profile directory."""
    if not THEMES_DIR.exists():
        return []
    themes = []
    for entry in sorted(THEMES_DIR.iterdir()):
        if entry.is_dir() and (entry / "assets").exists() and (entry / "README.md").exists():
            themes.append(entry.name)
    return themes


def hours_to_cron(hours):
    """Convert hours interval to cron expression."""
    hours = int(hours)
    if hours == 1:
        return "0 * * * *"
    elif 1 < hours < 24 and 24 % hours == 0:
        return f"0 */{hours} * * *"
    elif hours == 24:
        return "0 0 * * *"
    elif hours > 24 and hours % 24 == 0:
        days = hours // 24
        return f"0 0 */{days} * *"
    else:
        # Default to standard step
        return f"0 */{hours} * * *"


def update_workflow_cron(cron_expr):
    """Ensure .github/workflows/rotate-readme.yml has the matching cron expression."""
    if not WORKFLOW_FILE.exists():
        generate_workflow(cron_expr)
        return
    with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"(-\s*cron:\s*['\"][^'\"]+['\"])",
        f"- cron: '{cron_expr}'",
        content
    )
    if new_content != content:
        with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[Workflow] Updated GitHub Actions cron schedule to '{cron_expr}'")


def generate_workflow(cron_expr):
    """Generate the GitHub Actions workflow file if it does not exist."""
    WORKFLOW_FILE.parent.mkdir(parents=True, exist_ok=True)
    workflow_yaml = f"""name: Rotate Profile README

on:
  schedule:
    # Auto-rotate based on interval in profile-data.json
    - cron: '{cron_expr}'
  workflow_dispatch:
    inputs:
      theme:
        description: 'Specific theme to activate (leave empty for next in cycle)'
        required: false
        default: ''
      force:
        description: 'Force rotation even if not scheduled'
        type: boolean
        default: true
  push:
    paths:
      - 'profile-data.json'

permissions:
  contents: write

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Rotate Profile README
        run: |
          if [ -n "${{{{ github.event.inputs.theme }}}}" ]; then
            python rotate.py --theme "${{{{ github.event.inputs.theme }}}}"
          elif [ "${{{{ github.event_name }}}}" = "push" ]; then
            python rotate.py --sync
          else
            python rotate.py --next
          fi

      - name: Commit and push changes
        run: |
          git config --local user.name "github-actions[bot]"
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          if git diff --staged --quiet; then
            echo "No changes to commit."
          else
            CURRENT_THEME=$(python -c "import json; print(json.load(open('profile-data.json'))['rotation']['current_theme'])")
            git commit -m "Auto-rotate README to theme: ${{CURRENT_THEME}} [skip ci]"
            git push
          fi
"""
    with open(WORKFLOW_FILE, "w", encoding="utf-8") as f:
        f.write(workflow_yaml)
    print(f"[Workflow] Created GitHub Actions workflow at {WORKFLOW_FILE}")


def sanitize_and_render_readme(theme_name, template_text, data):
    """
    Renders a theme's README template by injecting the latest shared
    links, text, projects, and skills from profile-data.json.
    """
    content = template_text
    links = data.get("links", {})
    profile = data.get("profile", {})
    projects = data.get("projects", [])
    skills = data.get("skills", [])
    rotation = data.get("rotation", {})

    # 1. Update Core Links (GitHub, LinkedIn, Portfolio)
    github_url = links.get("github", "https://github.com/solacode-SC")
    linkedin_url = links.get("linkedin", "https://www.linkedin.com/in/solayman-elmouden/")
    portfolio_url = links.get("portfolio", "https://solaymanbuilds.com")
    portfolio_display = links.get("portfolio_display", "solaymanbuilds.com")
    handle = profile.get("handle", "solacode-SC")

    # Replace any LinkedIn placeholders or URLs
    content = re.sub(
        r"https://www\.linkedin\.com/in/(?:YOUR-LINKEDIN|[a-zA-Z0-9_\-]+/?)(?=['\"\s\)])",
        linkedin_url,
        content
    )

    # Replace any Portfolio placeholders or old URLs
    content = re.sub(
        r"https?://(?:solaymantech\.me|YOUR-PORTFOLIO)(?=['\"\s\)])",
        portfolio_url,
        content
    )
    content = re.sub(
        r"solaymantech\.me",
        portfolio_display,
        content
    )

    # 2. Update shields badges if present (preserving any trailing -HEXCOLOR)
    content = re.sub(
        r"https://img\.shields\.io/badge/LinkedIn-[^?]+?(-[0-9a-fA-F]{6})?(?=\?)",
        lambda m: f"https://img.shields.io/badge/LinkedIn-{profile.get('name', 'Solayman').replace(' ', '_')}{m.group(1) or ''}",
        content
    )
    content = re.sub(
        r"https://img\.shields\.io/badge/Portfolio-[^?]+?(-[0-9a-fA-F]{6})?(?=\?)",
        lambda m: f"https://img.shields.io/badge/Portfolio-{portfolio_display}{m.group(1) or ''}",
        content
    )

    # 3. Update Project URLs (live URLs take priority over repo URLs)
    for proj in projects:
        slug = proj.get("repo_slug") or proj.get("id")
        target_url = proj.get("live_url") or proj.get("repo_url")
        if slug and target_url:
            content = re.sub(
                rf"https://github\.com/[^/]+/{re.escape(slug)}(?=['\"\s\)])",
                target_url,
                content
            )

    # 4. For solacode-lilypond specific bio text paragraphs
    if theme_name == "solacode-lilypond":
        about_paras = profile.get("about", [])
        if len(about_paras) >= 2:
            about_block = f"{about_paras[0]}\n\n{about_paras[1]}"
            content = re.sub(
                r"I’m Solayman El Mouden, a software engineer focused on systems.*?\n\nI enjoy understanding how things work underneath the abstraction and turning that knowledge into useful software\.",
                about_block,
                content,
                flags=re.DOTALL
            )

    return content


def verify_theme(theme_name):
    """Verify that a theme exists, has its assets, and supports both dark and light modes."""
    theme_path = THEMES_DIR / theme_name
    if not theme_path.exists():
        return False, f"Theme directory '{theme_name}' does not exist"

    readme_path = theme_path / "README.md"
    if not readme_path.exists():
        return False, f"Theme '{theme_name}' is missing README.md"

    assets_path = theme_path / "assets"
    if not assets_path.exists():
        return False, f"Theme '{theme_name}' is missing assets/ directory"

    assets = list(assets_path.iterdir())
    if not assets:
        return False, f"Theme '{theme_name}' assets/ directory is empty"

    dark_assets = [f.name for f in assets if "dark" in f.name.lower()]
    light_assets = [f.name for f in assets if "light" in f.name.lower()]

    if not dark_assets:
        return False, f"Theme '{theme_name}' has no dark mode assets"
    if not light_assets:
        return False, f"Theme '{theme_name}' has no light mode assets"

    # Check for missing references in README.md
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_text = f.read()

    refs = set(re.findall(r'(?:assets/|\./assets/)([a-zA-Z0-9_\-\.]+)', readme_text))
    existing_assets = {f.name for f in assets}
    missing = refs - existing_assets
    if missing:
        return False, f"Theme '{theme_name}' references missing assets: {missing}"

    unused_cards = {f for f in existing_assets if f.startswith("card-") and f not in refs}
    if unused_cards:
        return False, f"Theme '{theme_name}' has unreferenced card assets: {sorted(unused_cards)}"

    return True, f"OK ({len(assets)} assets: {len(dark_assets)} dark, {len(light_assets)} light)"


def sync_all_templates(data=None):
    """
    Sync all templates in other-profile/ with the latest shared links and info
    from profile-data.json, ensuring no broken placeholders remain.
    """
    if data is None:
        data = load_data()

    themes = get_available_themes()
    print(f"\n[Sync] Synchronizing {len(themes)} themes with shared profile data...")

    for theme in themes:
        readme_path = THEMES_DIR / theme / "README.md"
        if not readme_path.exists():
            continue
        with open(readme_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        updated_text = sanitize_and_render_readme(theme, raw_text, data)
        if updated_text != raw_text:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(updated_text)
            print(f"  ✓ Updated {theme}/README.md")
        else:
            print(f"  • Up to date: {theme}/README.md")

    # Also sync root README if current_theme is active
    current_theme = data.get("rotation", {}).get("current_theme")
    if current_theme and README_FILE.exists():
        with open(README_FILE, "r", encoding="utf-8") as f:
            root_text = f.read()
        updated_root = sanitize_and_render_readme(current_theme, root_text, data)
        if updated_root != root_text:
            with open(README_FILE, "w", encoding="utf-8") as f:
                f.write(updated_root)
            print(f"  ✓ Updated root README.md")

    # Sync workflow cron
    cron_expr = data.get("rotation", {}).get("cron") or hours_to_cron(data.get("rotation", {}).get("interval_hours", 12))
    update_workflow_cron(cron_expr)
    print("[Sync] All themes and configurations are in sync!\n")


def apply_theme(theme_name, data=None):
    """
    Deploy the specified theme to the repository root:
    1. Replaces root assets/ with the theme's assets/
    2. Renders and writes root README.md
    3. Updates profile-data.json rotation state
    """
    if data is None:
        data = load_data()

    theme_path = THEMES_DIR / theme_name
    if not theme_path.exists():
        sys.exit(f"Error: Theme '{theme_name}' does not exist in {THEMES_DIR}")

    valid, msg = verify_theme(theme_name)
    if not valid:
        sys.exit(f"Error verifying theme '{theme_name}': {msg}")

    print(f"Applying theme: '{theme_name}'")

    # 1. Update root assets/ directory
    theme_assets = theme_path / "assets"
    if ASSETS_DIR.exists():
        shutil.rmtree(ASSETS_DIR)
    shutil.copytree(theme_assets, ASSETS_DIR)
    print(f"  ✓ Deployed {len(list(ASSETS_DIR.iterdir()))} SVG assets to ./assets/")

    # 2. Read, render, and deploy README.md
    theme_readme = theme_path / "README.md"
    with open(theme_readme, "r", encoding="utf-8") as f:
        template_text = f.read()

    rendered_readme = sanitize_and_render_readme(theme_name, template_text, data)

    # Ensure relative asset paths work nicely from root
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(rendered_readme)
    print(f"  ✓ Deployed rendered README.md to repository root")

    # 3. Update rotation state in profile-data.json
    collection = data.get("rotation", {}).get("collection", get_available_themes())
    if theme_name in collection:
        index = collection.index(theme_name)
    else:
        collection.append(theme_name)
        index = len(collection) - 1

    data["rotation"]["current_theme"] = theme_name
    data["rotation"]["current_index"] = index
    data["rotation"]["last_rotated"] = datetime.now(timezone.utc).isoformat()
    save_data(data)
    print(f"  ✓ Updated profile-data.json state (index: {index}, theme: {theme_name})")
    print(f"\n[Success] Profile theme is now '{theme_name}'! Dark & light modes active.\n")


def rotate_next(data=None):
    """Advance to the next theme in the configured collection."""
    if data is None:
        data = load_data()

    collection = data.get("rotation", {}).get("collection", [])
    if not collection:
        collection = get_available_themes()
        data["rotation"]["collection"] = collection

    if not collection:
        sys.exit("Error: No themes found in other-profile/")

    current_theme = data.get("rotation", {}).get("current_theme")
    mode = data.get("rotation", {}).get("mode", "sequential")

    if mode == "random":
        import random
        candidates = [t for t in collection if t != current_theme]
        next_theme = random.choice(candidates if candidates else collection)
    else:
        # Sequential
        try:
            current_index = collection.index(current_theme)
            next_index = (current_index + 1) % len(collection)
        except ValueError:
            next_index = 0
        next_theme = collection[next_index]

    print(f"[Rotate] Advancing from '{current_theme}' -> '{next_theme}'")
    apply_theme(next_theme, data)


def display_status(data=None):
    """Display comprehensive status of rotation system."""
    if data is None:
        data = load_data()

    rotation = data.get("rotation", {})
    profile = data.get("profile", {})
    links = data.get("links", {})
    current_theme = rotation.get("current_theme", "unknown")
    interval = rotation.get("interval_hours", 12)
    cron_expr = rotation.get("cron", "0 */12 * * *")
    last_rotated = rotation.get("last_rotated", "never")
    collection = rotation.get("collection", [])

    print("=" * 68)
    print("      Solayman El Mouden - Profile README Rotation Status")
    print("=" * 68)
    print(f"  Current Theme    : {current_theme}")
    meta = rotation.get("theme_metadata", {}).get(current_theme, {})
    if meta:
        print(f"  Theme Name       : {meta.get('name')}")
        print(f"  Theme Description: {meta.get('description')}")
    print(f"  Rotation Interval: Every {interval} hours (cron: '{cron_expr}')")
    print(f"  Rotation Mode    : {rotation.get('mode', 'sequential')}")
    print(f"  Last Rotated At  : {last_rotated}")

    # Calculate next theme
    try:
        curr_idx = collection.index(current_theme)
        next_theme = collection[(curr_idx + 1) % len(collection)]
        print(f"  Next Theme       : {next_theme} (cycle position: {curr_idx + 1}/{len(collection)})")
    except ValueError:
        print(f"  Next Theme       : (theme not in current collection list)")

    print("-" * 68)
    print(f"  Shared Profile Data:")
    print(f"    • Name         : {profile.get('name')}")
    print(f"    • Role         : {profile.get('role')}")
    print(f"    • GitHub       : {links.get('github')}")
    print(f"    • LinkedIn     : {links.get('linkedin')}")
    print(f"    • Portfolio    : {links.get('portfolio')}")
    print(f"    • Projects     : {len(data.get('projects', []))} configured")
    print(f"    • Skills       : {len(data.get('skills', []))} configured")
    print("-" * 68)
    print(f"  Theme Collection ({len(collection)} total):")
    for i, t in enumerate(collection, 1):
        marker = "★ [ACTIVE]" if t == current_theme else " "
        print(f"    {i:2d}. {t:<28} {marker}")
    print("=" * 68)


def list_themes():
    """List all available themes with their metadata."""
    data = load_data()
    collection = data.get("rotation", {}).get("collection", [])
    current = data.get("rotation", {}).get("current_theme")
    metadata = data.get("rotation", {}).get("theme_metadata", {})

    print("\nAvailable Profile Themes in 'other-profile/':")
    print("-" * 72)
    for theme in get_available_themes():
        valid, msg = verify_theme(theme)
        status_tag = "[OK]" if valid else f"[INVALID: {msg}]"
        active_tag = " -> CURRENT ACTIVE" if theme == current else ""
        meta = metadata.get(theme, {})
        title = meta.get("name", theme)
        desc = meta.get("description", "")
        print(f" • {theme:<26} {status_tag}{active_tag}")
        if title != theme:
            print(f"     Title: {title}")
        if desc:
            print(f"     Info : {desc}")
    print("-" * 72 + "\n")


def set_interval(hours):
    """Update rotation interval in hours and sync with workflow cron."""
    data = load_data()
    data["rotation"]["interval_hours"] = hours
    cron_expr = hours_to_cron(hours)
    data["rotation"]["cron"] = cron_expr
    save_data(data)
    update_workflow_cron(cron_expr)
    print(f"[Interval] Rotation interval set to {hours} hours (cron: '{cron_expr}')")


def verify_all():
    """Run full verification on all themes and assets."""
    themes = get_available_themes()
    print("\nVerifying all themes and dark/light mode compatibility:")
    print("-" * 70)
    all_ok = True
    for theme in themes:
        valid, msg = verify_theme(theme)
        prefix = "  ✓" if valid else "  ✗"
        print(f"{prefix} {theme:<26} : {msg}")
        if not valid:
            all_ok = False
    print("-" * 70)
    if all_ok:
        print("All themes passed verification! Both light and dark modes are ready.\n")
    else:
        print("Some themes had issues. See details above.\n")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Profile README Rotation System")
    parser.add_argument("--next", action="store_true", help="Rotate to next theme in cycle")
    parser.add_argument("--theme", type=str, help="Apply a specific theme directly")
    parser.add_argument("--status", action="store_true", help="Show current rotation status")
    parser.add_argument("--list", action="store_true", help="List all available themes")
    parser.add_argument("--sync", action="store_true", help="Sync all theme templates with profile-data.json")
    parser.add_argument("--interval", type=int, help="Update rotation cycle duration in hours")
    parser.add_argument("--verify", action="store_true", help="Verify themes and dark/light mode assets")

    args = parser.parse_args()

    # Default action if no arguments provided: show status
    if len(sys.argv) == 1:
        display_status()
        return

    if args.interval is not None:
        set_interval(args.interval)

    if args.sync:
        sync_all_templates()

    if args.verify:
        verify_all()

    if args.list:
        list_themes()

    if args.theme:
        apply_theme(args.theme)

    if args.next:
        rotate_next()

    if args.status:
        display_status()


if __name__ == "__main__":
    main()
