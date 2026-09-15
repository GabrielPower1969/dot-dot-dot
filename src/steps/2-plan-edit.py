#!/usr/bin/env python3
"""Step 2: transcript + voiceover.md + edit.json(optional) -> work/plan.json

  * retake detection  : a later phrase that repeats an earlier one => cut from the false start to the restart
  * silence tightening: gaps between words longer than cut.silence_gap_s shrink to cut.silence_keep_s
  * script alignment  : ASR characters are diff-aligned to the SCRIPT so subtitles show the author's text
  * anchors           : edit.json items say WHERE with a quote from the script ("anchor": "温水煮青蛙"),
                        this step turns them into source + output times
"""
import sys, re, json, difflib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import load_project, read_json, write_json, die
from lib.timeline import Timeline, invert, merge, apply_speed

PUNCT = "，。！？；：、,.!?;:\"'“”‘’（）()《》〈〉【】[]—…- \n\t"
def clean(s): return "".join(ch for ch in s if ch not in PUNCT)

# ---------- script ----------
def load_script(path):
    """Return (display_text, inserts). Strips markdown; pulls '(后期提示：...)' notes out as inserts."""
    txt = Path(path).read_text(encoding="utf-8")
    txt = re.sub(r"^#+\s*", "", txt, flags=re.M)
    txt = txt.replace("**", "").replace("  \n", "\n")
    notes = []
    def grab(m):
        notes.append({"note": m.group(1).strip(), "at_char": len(clean(txt[:m.start()]))}); return ""
    txt = re.sub(r"[（(]\s*后期提示\s*[:：]\s*(.*?)[)）]", grab, txt)
    txt = re.sub(r"\n{2,}", "\n", txt).strip()
    return txt, notes

def split_cues(text, max_chars):
    """Sentences -> clauses -> hard wrap. Returns list of (text, clean_start_idx, clean_len)."""
    cues, pos = [], 0
    for sent in re.split(r"(?<=[。！？!?；;\n])", text):
        sent = sent.strip("\n")
        if not clean(sent): pos += len(clean(sent)); continue
        parts = [p for p in re.split(r"(?<=[，,、：:])", sent) if p]
        buf = ""
        def flush():
            nonlocal buf, pos
            if clean(buf):
                cues.append({"text": buf.strip(" "), "c0": pos, "clen": len(clean(buf))}); pos += len(clean(buf))
            buf = ""
        for part in parts:
            if len(clean(buf)) + len(clean(part)) > max_chars and buf: flush()
            if len(clean(part)) > max_chars:  # balanced wrap of a long clause (no orphan chars)
                flush()
                cp = clean(part); n = -(-len(cp) // max_chars); size = -(-len(cp) // n)
                for i in range(0, len(cp), size):
                    chunk = cp[i:i+size]
                    cues.append({"text": chunk, "c0": pos, "clen": len(chunk)}); pos += len(chunk)
            else: buf += part
        flush()
    return cues

# ---------- transcript ----------
def load_words(tj):
    words = []
    for s in tj["segments"]:
        for w in s.get("words", []):
            t = clean(w["word"])
            if t: words.append({"t": t, "s": float(w["start"]), "e": float(w["end"]), "seg": s["id"]})
    return words

def detect_retakes(segs, cfg):
    """Return cut intervals [(a,b,why)]: from the start of a false start to the start of its redo.
    A candidate pair (i, j) needs the first phrase to repeat AND the whole false-start run [i, j) to
    repeat in what follows j — this rejects '第一个就是…' vs '第二个就是…' style false positives."""
    cuts, i = [], 0
    texts = [clean(s["text"]) for s in segs]
    while i < len(segs):
        ta, found = texts[i], None
        if len(ta) >= 4:
            for j in range(i+1, len(segs)):
                if segs[j]["start"] - segs[i]["end"] > cfg["retake_window_s"]: break
                tb = texts[j]
                if len(tb) < 4: continue
                r1 = difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()
                if r1 < cfg["retake_similarity"]: continue
                run = "".join(texts[i:j]); L = min(len(run), 24)
                redo = "".join(texts[j:j+8])[:L]
                r2 = difflib.SequenceMatcher(None, run[:L], redo, autojunk=False).ratio()
                if r2 >= cfg["retake_similarity"]:
                    found = (j, r1, r2); break
        if found:
            j, r1, r2 = found
            cuts.append((max(0.0, segs[i]["start"] - 0.08), segs[j]["start"] - cfg["pad_before_s"],
                         f"retake: '{ta[:12]}…' ({j-i} phrase(s)) redone at {segs[j]['start']:.1f}s (sim {r1:.2f}/{r2:.2f})"))
            i = j
        else: i += 1
    return cuts

def silence_cuts(words, cfg, total):
    cuts = []
    if words and words[0]["s"] > cfg["silence_keep_s"] + cfg["pad_before_s"]:
        cuts.append((0.0, words[0]["s"] - cfg["pad_before_s"], "leading silence"))
    for w1, w2 in zip(words, words[1:]):
        gap = w2["s"] - w1["e"]
        if gap > cfg["silence_gap_s"]:
            a = w1["e"] + cfg["pad_after_s"]; b = w2["s"] - cfg["pad_before_s"]
            keep = cfg["silence_keep_s"]
            if b - a > keep: cuts.append((a + keep/2, b - keep/2, f"silence {gap:.2f}s"))
    if words and total - words[-1]["e"] > 1.0:
        cuts.append((words[-1]["e"] + 0.6, total, "trailing silence"))
    return cuts

# ---------- alignment ----------
def align(words, script_clean):
    asr = "".join(w["t"] for w in words)
    idx = []  # asr char -> word index
    for wi, w in enumerate(words): idx += [wi] * len(w["t"])
    sm = difflib.SequenceMatcher(None, asr, script_clean, autojunk=False)
    t_of = [None] * len(script_clean)  # script char -> (start,end)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w = words[idx[blk.a + k]]
            n = len(w["t"]); off = (blk.a + k) - sum(len(x["t"]) for x in words[:idx[blk.a+k]])
            s = w["s"] + (w["e"] - w["s"]) * off / n; e = w["s"] + (w["e"] - w["s"]) * (off+1) / n
            t_of[blk.b + k] = (s, e)
    matched = sum(1 for x in t_of if x)
    # interpolate gaps
    last = None
    for i in range(len(t_of)):
        if t_of[i]: last = i; continue
        nxt = next((j for j in range(i+1, len(t_of)) if t_of[j]), None)
        if last is not None and nxt is not None:
            a, b = t_of[last][1], t_of[nxt][0]; span = nxt - last
            s = a + (b - a) * (i - last - 0.5) / span; e = a + (b - a) * (i - last + 0.5) / span
            t_of[i] = (s, e, "interp")
        elif last is not None: t_of[i] = (t_of[last][1], t_of[last][1] + 0.2, "interp")
        elif nxt is not None: t_of[i] = (t_of[nxt][0] - 0.2, t_of[nxt][0], "interp")
    return t_of, matched / max(1, len(script_clean)), sm.ratio()

def anchor_time(script_clean, t_of, quote, occurrence=1):
    q = clean(quote); pos, start = -1, 0
    for _ in range(occurrence):
        pos = script_clean.find(q, start)
        if pos < 0: return None
        start = pos + 1
    return t_of[pos][0], t_of[pos + len(q) - 1][1]

# ---------- main ----------
def main():
    P = load_project(sys.argv[1]); prof = P["profile"]; cfg = prof["cut"]
    tj = read_json(P["work"]/"transcript.json")
    edit = read_json(P["edit"]) if P["edit"] else {}
    words = load_words(tj)
    total = max(w["e"] for w in words) + 1.0
    import subprocess
    dur = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(P["source"])],capture_output=True,text=True).stdout.strip()
    total = float(dur) if dur else total

    # 1. cuts
    cuts = detect_retakes(tj["segments"], cfg)
    for mc in edit.get("manual_cuts", []):
        cuts.append((mc["from_s"], mc["to_s"], "manual: " + mc.get("why", "")))
    cut_iv = merge([(a, b) for a, b, _ in cuts])
    kept_words = [w for w in words if not any(a <= (w["s"]+w["e"])/2 <= b for a, b in cut_iv)]
    sil = silence_cuts(kept_words, cfg, total)
    all_cuts = merge(cut_iv + [(a, b) for a, b, _ in sil])
    ramps = [(r["from_s"], r["to_s"], float(r["factor"])) for r in edit.get("speed", [])]  # slow-mo 0.5, fast 2.0 ...
    keeps = apply_speed(invert(all_cuts, total), ramps)
    TL = Timeline(keeps)

    # 2. align script
    script_text, notes = load_script(P["voiceover"])
    sc = clean(script_text)
    t_of, coverage, ratio = align(kept_words, sc)

    # 3. cues
    lang = prof["creator"]["default_language"]
    cues = []
    for i, c in enumerate(split_cues(script_text, prof["subtitles"][f"max_chars_{lang}"])):
        span = t_of[c["c0"]:c["c0"]+c["clen"]]
        real = [x for x in span if len(x) == 2]
        if len(real) < max(1, 0.3 * len(span)):  # speaker skipped this line
            cues.append({"id": i, "text": c["text"], "skipped": True}); continue
        s, e = span[0][0], span[-1][1]
        cues.append({"id": i, "text": c["text"], "src_s": round(s, 3), "src_e": round(e, 3),
                     "s": round(TL.to_out(s), 3), "e": round(TL.to_out(e), 3)})
    live = [c for c in cues if not c.get("skipped")]
    for c1, c2 in zip(live, live[1:]):  # close small gaps, avoid overlap
        if c2["s"] - c1["e"] < 0.6: c1["e"] = round(c2["s"] - 0.04, 3)
        if c1["e"] - c1["s"] < 0.7: c1["e"] = round(min(c1["s"] + 0.7, c2["s"] - 0.04), 3)

    # 4. anchors -> events
    def resolve(item):
        if "at_s" in item: s = item["at_s"]; e = s + item.get("hold_s", 1.5)
        else:
            r = anchor_time(sc, t_of, item["anchor"], item.get("occurrence", 1))
            if not r: print(f"WARN: anchor not found in script: {item['anchor']!r}"); return None
            s, e = r
            if "hold_s" in item: e = s + item["hold_s"]
        if TL.is_cut(s): print(f"WARN: anchor {item.get('anchor')} lies in a cut"); return None
        return {**item, "src_s": round(s, 3), "src_e": round(e, 3), "s": round(TL.to_out(s), 3), "e": round(TL.to_out(e), 3)}
    pops = [x for x in (resolve(p) for p in edit.get("pops", [])) if x]
    inserts = [x for x in (resolve(p) for p in edit.get("inserts", [])) if x]
    sfx = [x for x in (resolve(p) for p in edit.get("sfx", [])) if x]
    for n in notes:  # script-side notes become TODO inserts if edit.json didn't cover them
        n["src_s"] = round(t_of[min(n["at_char"], len(t_of)-1)][0], 3); n["s"] = round(TL.to_out(n["src_s"]), 3)

    plan = {
        "slug": P["slug"], "source": str(P["source"]), "source_duration": total, "out_duration": round(TL.duration, 3),
        "keeps": [[round(a,3), round(b,3), sp] for a, b, sp in keeps],
        "cuts": [{"from_s": round(a,3), "to_s": round(b,3), "why": w} for a, b, w in sorted(cuts + sil)],
        "alignment": {"script_coverage": round(coverage, 3), "asr_script_ratio": round(ratio, 3), "words": len(kept_words)},
        "cues": {lang: cues}, "pops": pops, "inserts": inserts, "sfx": sfx, "script_notes": notes,
        "intro": edit.get("intro"), "outro": edit.get("outro", {}),
    }
    write_json(P["work"]/"plan.json", plan)
    n_cut = sum(b - a for a, b in all_cuts)
    print(f"OK: {len(cuts)} retake/manual cuts, {len(sil)} silence trims, removed {n_cut:.1f}s -> {TL.duration:.1f}s "
          f"| script coverage {coverage:.0%} | {len(live)} cues, {len(pops)} pops, {len(inserts)} inserts")
    for a, b, w in cuts: print(f"   cut {a:7.2f}-{b:7.2f}  {w}")
    for n in notes: print(f"   script note @{n['s']:.1f}s: {n['note']}")
if __name__ == "__main__": main()
