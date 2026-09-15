#!/usr/bin/env python3
"""Step 2b: work/plan.json zh cues -> projects/<slug>/cues.en.json via the 'translate' LLM route.
Skips cues already translated (file is keyed by zh text, so edits survive re-splits). Without API keys it
prints the missing cues so a human/agent can fill the file by hand."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import load_project, read_json, write_json
from llm.router import call, LLMError

def main():
    P = load_project(sys.argv[1]); plan = read_json(P["work"]/"plan.json")
    f = P["dir"]/"cues.en.json"; done = read_json(f) if f.exists() else {}
    todo = [c["text"] for c in plan["cues"]["zh"] if not c.get("skipped") and c["text"] not in done]
    if not todo: print("OK: all cues translated"); return
    prompt = ("Translate each Chinese subtitle line to natural spoken English for on-screen subtitles. Keep each line short "
              "(<= 42 chars where possible), keep the line order, keep numbering words, no commentary. Return JSON object {zh: en}.\n\n"
              + json.dumps(todo, ensure_ascii=False))
    try:
        text = call("translate", prompt, max_tokens=4000)
        got = json.loads(text[text.find("{"):text.rfind("}")+1])
        done.update({k: v for k, v in got.items() if k in todo}); write_json(f, done)
        print(f"OK: translated {len(got)} cues -> {f}")
    except (LLMError, ValueError) as e:
        print(f"no LLM available ({e}). Fill these {len(todo)} cues in {f} by hand:"); [print("  ", t) for t in todo]; sys.exit(2)
if __name__ == "__main__": main()
