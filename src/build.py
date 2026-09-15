#!/usr/bin/env python3
"""THE command:  python3 src/build.py projects/<slug>  [--force]
1 transcribe -> 2 plan -> 2b translate (needs cues.en.json or an LLM key) -> 3 cards -> 4 assemble -> 5 package.
Stops at the first failing step. Every step is re-runnable alone (see package.json scripts)."""
import sys, subprocess, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def need(tool):
    if not shutil.which(tool): print(f"FAIL: {tool} not installed (brew install {tool})"); sys.exit(1)
for t in ("ffmpeg", "ffprobe", "node"): need(t)
if not (ROOT/"node_modules/playwright").exists(): print("FAIL: run `npm install` first (Playwright renders cards/covers)"); sys.exit(1)
proj = sys.argv[1]; extra = sys.argv[2:]
steps = [["python3", "src/steps/1-transcribe.py"], ["python3", "src/steps/2-plan-edit.py"], ["python3", "src/steps/2b-translate.py"],
         ["node", "src/steps/3-render-cards.js"], ["python3", "src/steps/4-assemble.py"], ["python3", "src/steps/5b-titles.py"], ["node", "src/steps/5-package.js"]]
for s in steps:
    print(f"\n== {s[1]}"); r = subprocess.run([*s, proj, *extra], cwd=ROOT)
    if r.returncode not in (0, 2): sys.exit(r.returncode)   # 2 = translate needs a human; keep going
print("\nDONE ->", Path(proj).name, "/output")
