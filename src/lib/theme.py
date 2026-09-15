"""Resolve profile.brand.theme -> colour tokens (config/themes.json). Shared by ASS builder and card/cover renderers (via _theme.css)."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def load(profile):
    themes = json.loads((ROOT/"config/themes.json").read_text())
    name = profile["brand"].get("theme", "ink-classic"); t = dict(themes[name]); t["name"] = name; return t
def css(t):
    return (f":root{{--paper:{t['paper']};--paper-2:{t['paper2']};--ink:{t['ink']};--muted:{t['muted']};--line:{t['line']};"
            f"--accent:{t['accent']};--accent-soft:{t['accentSoft']};--accent-on:{t['accentOn']};--mode:{t['mode']}}}\n")
def write_css(profile):
    t = load(profile); (ROOT/"templates/cards/_theme.css").write_text(css(t)); return t
