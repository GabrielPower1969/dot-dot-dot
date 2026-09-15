#!/usr/bin/env python3
"""Step 1: source video -> work/transcript.json (word timestamps) + work/audio16k.wav.
Local mlx-whisper only. Never uploads audio anywhere."""
import sys, os, json, shutil, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import load_project, sh, die, ROOT

def find_python_with_mlx():
    cands = [os.environ.get("CM_WHISPER_PYTHON"), str(ROOT/".venv/bin/python")]
    cands += [str(p) for p in Path(ROOT).parent.glob("*/.venv/bin/python")]
    for c in cands:
        if c and Path(c).exists():
            r = subprocess.run([c, "-c", "import mlx_whisper"], capture_output=True)
            if r.returncode == 0: return c
    die("no python with mlx_whisper. Run: python3 -m venv .venv && .venv/bin/pip install mlx-whisper")

def main():
    P = load_project(sys.argv[1]); P["work"].mkdir(exist_ok=True)
    wav, out = P["work"]/"audio16k.wav", P["work"]/"transcript.json"
    if out.exists() and "--force" not in sys.argv:
        print(f"skip: {out} exists (use --force)"); return
    sh(["ffmpeg", "-v", "error", "-y", "-i", P["source"], "-vn", "-ac", "1", "-ar", "16000", wav])
    lang = P["profile"]["creator"]["default_language"]
    hint = Path(P["script"]).read_text(encoding="utf-8")[:300].replace("\n", " ")
    code = f"""
import json, mlx_whisper
r = mlx_whisper.transcribe({str(wav)!r}, path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
    language={lang!r}, word_timestamps=True, condition_on_previous_text=False, initial_prompt={hint!r})
json.dump(r, open({str(out)!r}, "w"), ensure_ascii=False, indent=1)
"""
    sh([find_python_with_mlx(), "-c", code])
    segs = json.loads(out.read_text())["segments"]
    # hallucination check (repeated identical lines)
    texts = [s["text"].strip() for s in segs]
    rep = max((texts.count(t) for t in set(texts)), default=0)
    if rep >= 4: print(f"WARN: a line repeats {rep}x — possible Whisper hallucination, inspect {out}")
    print(f"OK: {len(segs)} segments -> {out}")
if __name__ == "__main__": main()
