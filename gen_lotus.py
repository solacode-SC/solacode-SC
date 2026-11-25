#!/usr/bin/env python3
"""Delegate to the authoritative Lily Pond generator in other-profile/solacode-lilypond/gen_lotus.py."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "other-profile" / "solacode-lilypond" / "gen_lotus.py"), run_name="__main__")
