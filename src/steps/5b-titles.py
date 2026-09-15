#!/usr/bin/env python3
"""Step 5b: auto-write copy.json (titles, hook, body, hashtags per platform, cover title options) from script + edit.json
via the LLM router (routes copy_zh / copy_en). Runs when copy.json is missing or with --regen. Keeps any existing
'cover' blocks (frame/font/style are the creator's). Without API keys it prints the prompt so the desktop agent can answer."""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import load_project, read_json, write_json, ROOT
from llm.router import call, LLMError

def main():
    P = load_project(sys.argv[1]); f = P["dir"]/"copy.json"
    if f.exists() and "--regen" not in sys.argv: print("skip: copy.json exists (use --regen)"); return
    old = read_json(f) if f.exists() else {}
    edit = read_json(P["edit"]) if P["edit"] else {}; script = Path(P["script"]).read_text(encoding="utf-8")[:6000]
    plats = P["platforms"]; limits = {k: {"title_max": v["title_max"], "tags_max": v["tags_max"], "languages": v["languages"]} for k, v in plats.items() if not k.startswith("$")}
    out = {"topic": old.get("topic") or P["slug"][11:], "cover_time_s": old.get("cover_time_s", 3), "publish_order": old.get("publish_order") or [k for k in limits], "schedule": old.get("schedule", ""), "platforms": {}}
    for lang in P["profile"]["creator"]["languages"]:
        prompt = f"""You write social copy for a face-on-camera creator. Language: {lang}. Video title: {json.dumps(edit.get('title', {}), ensure_ascii=False)}.
Script:\n{script}\n
Return ONLY JSON: {{"kicker": "<=10 chars situation label", "cover_title": "<=12 zh chars / <=6 en words claim, not the title", "cover_title_html": "same with <br> and one <em>word</em>",
"title": "post title <=60 chars, curiosity gap, no clickbait words", "hook": "first line", "body": "3 short lines with \\n", "cta": "one question", "hashtags": ["8 tags, 3 broad 3 niche 1 place, no #"],
"title_options": ["3 alternative cover titles as html"]}}"""
        try: text = call("copy_" + lang, prompt, max_tokens=1200); c = json.loads(text[text.find("{"):text.rfind("}")+1])
        except (LLMError, ValueError) as e: print(f"no LLM for {lang} ({e}).\n--- prompt ---\n{prompt}\n--------------"); sys.exit(2)
        c["cover"] = (old.get(lang) or {}).get("cover") or {"frame_s": out["cover_time_s"], "kicker": c["kicker"], "title_html": c["cover_title_html"], "title_options": c.get("title_options", []), "variants": [{"font": "noto-serif" if lang == "zh" else "playfair", "style": "editorial"}, {"font": "noto-light" if lang == "zh" else "inter", "style": "swiss"}, {"font": "noto-serif" if lang == "zh" else "playfair", "style": "photo"}], "pick": 1}
        out[lang] = c
    # per-platform titles within limits
    for pf, lim in limits.items():
        lang = lim["languages"][0]; c = out.get(lang); 
        if not c: continue
        prompt = f"Platform {pf}: title max {lim['title_max'] or 'none (body-only)'} chars, {lim['tags_max']} hashtags. Base title: {c['title']}. Base tags: {c['hashtags']}. Return ONLY JSON {{\"title\": \"...\", \"hashtags\": [..]}} adapted to this platform's culture ({lang})."
        try: text = call("copy_" + lang, prompt, max_tokens=300); out["platforms"][pf] = json.loads(text[text.find("{"):text.rfind("}")+1])
        except (LLMError, ValueError): out["platforms"][pf] = old.get("platforms", {}).get(pf, {})
    write_json(f, out); print(f"OK: wrote {f}")
if __name__ == "__main__": main()
