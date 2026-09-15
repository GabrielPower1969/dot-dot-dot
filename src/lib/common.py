"""Shared helpers: paths, json, project loading. stdlib only."""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def write_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

def die(msg, code=1):
    print(f"FAIL: {msg}", file=sys.stderr); sys.exit(code)

SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")

def load_project(arg):
    """arg = projects/<slug> or <slug>. Returns dict with paths."""
    p = Path(arg)
    if not p.exists(): p = ROOT / "projects" / arg
    if not p.is_dir(): die(f"project dir not found: {arg}")
    slug = p.name
    if not SLUG_RE.match(slug): die(f"bad slug '{slug}': want <yyyy-mm-dd>-<topic>")
    src = sorted(list((p/"source").glob("*.mp4")) + list((p/"source").glob("*.mov")))
    if not src: die(f"{p}/source/ has no .mp4/.mov")
    return {
        "slug": slug, "dir": p, "source": src[0], "work": p/"work", "output": p/"output",
        "script": p/"script.md", "voiceover": p/"voiceover.md" if (p/"voiceover.md").exists() else p/"script.md",
        "edit": p/"edit.json" if (p/"edit.json").exists() else None,
        "profile": read_json(ROOT/"config/profile.json"),
        "platforms": read_json(ROOT/"config/platforms.json"),
    }

def sh(cmd, check=True, quiet=False):
    import subprocess
    if not quiet: print("  $", " ".join(str(c) for c in cmd)[:300])
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if check and r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr); die(f"command failed: {cmd[0]}")
    return r
