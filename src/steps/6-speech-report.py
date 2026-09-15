#!/usr/bin/env python3
"""Step 6 (speech-coach): delivery analysis of the RAW take -> work/speech-report.html
pace per phrase, gaps, fillers, breath points (low-level broadband bursts in gaps), lip smacks / mouth clicks
(very short transients in gaps), end-of-sentence energy. Heuristics — labelled as such in the report.
Needs numpy (any python; the whisper venv has it)."""
import sys, json, re, wave, html, subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import load_project, read_json

FILLERS = ["啊", "呃", "嗯", "那个", "就是", "然后", "其实", "对"]
def clean(s): return re.sub(r"[，。！？；：、,.!?;:\"'“”‘’（）()《》—…\s]", "", s)

def main():
    P = load_project(sys.argv[1]); W = P["work"]
    tj = read_json(W/"transcript.json"); plan = read_json(W/"plan.json") if (W/"plan.json").exists() else {"cuts": []}
    with wave.open(str(W/"audio16k.wav")) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(sr * 0.01); n = len(x) // hop
    fr = x[:n*hop].reshape(n, hop)
    rms = 20*np.log10(np.sqrt((fr**2).mean(1)) + 1e-9)            # dBFS per 10 ms
    zcr = (np.abs(np.diff(np.sign(fr), axis=1)) > 0).mean(1)      # zero-crossing rate (breath = high, voice = low)
    peak = 20*np.log10(np.abs(fr).max(1) + 1e-9)
    def t2i(t): return min(n-1, max(0, int(t*100)))
    segs = tj["segments"]; words = [w for s in segs for w in s.get("words", [])]
    cut_spans = [(c["from_s"], c["to_s"], c["why"]) for c in plan.get("cuts", []) if "retake" in c["why"] or "manual" in c["why"]]
    def in_cut(t): return any(a <= t <= b for a, b, _ in cut_spans)

    # --- pauses from energy (whisper word times swallow silence, so gaps must come from audio) ---
    sil = rms < -42
    pauses = []; k = 0
    while k < n:
        if sil[k]:
            j = k
            while j < n and sil[j]: j += 1
            if (j - k) >= 15: pauses.append((k/100, j/100))
            k = j
        else: k += 1
    def pause_after(t_end, t_next):
        ps = [(a, b) for a, b in pauses if b > t_end - 1.2 and a < t_next + 0.05]
        return (ps[-1][1] - ps[-1][0]) if ps else 0.0
    def voiced_dur(t0, t1):
        return (t1 - t0) - sum(max(0.0, min(b, t1) - max(a, t0)) for a, b in pauses if b > t0 and a < t1)
    # --- per phrase ---
    rows = []
    for i, s in enumerate(segs):
        txt = s["text"].strip(); ch = len(clean(txt))
        nxt = segs[i+1]["start"] if i+1 < len(segs) else s["end"] + 1
        gap = pause_after(s["end"], nxt); vd = max(0.2, voiced_dur(s["start"], s["end"]))
        a, b = t2i(s["start"]), t2i(s["end"]); body = rms[a:b]; voiced = body[body > -40]
        tail = voiced[-25:] if len(voiced) >= 25 else voiced
        drop = float(tail.mean() - voiced.mean()) if len(voiced) else 0.0
        fill = [f for f in FILLERS if clean(txt).startswith(f)]
        rows.append({"i": i, "s": s["start"], "e": s["end"], "text": txt, "chars": ch, "dur": vd, "cps": ch/vd,
                     "gap": gap, "tail_drop_db": drop, "filler_start": fill, "in_cut": in_cut((s["start"]+s["end"])/2)})
    # --- events inside pauses: breaths & clicks ---
    breaths, clicks = [], []
    word_ends = [w["end"] for w in words]
    for (g0, g1) in pauses:
        a, b = t2i(g0), t2i(g1); r, z, pk = rms[a:b], zcr[a:b], peak[a:b]
        m = (r > -52) & (r < -26) & (z > 0.18)
        run = 0; start = None
        for k, v in enumerate(m):
            if v: run += 1; start = start if start is not None else k
            if (not v or k == len(m)-1) and run >= 6:
                # in-clause = the pause sits between two words closer than 0.45 s (whisper says same sentence)
                seg = next((sg for sg in segs if sg["start"] - 0.05 <= g0 <= sg["end"] + 0.05), None)
                breaths.append({"t": g0 + start/100, "d": run/100, "db": float(r[start:start+run].mean()), "in_clause": seg is not None and g0 > seg["start"] + 0.2 and g1 < seg["end"] - 0.2}); run = 0; start = None
            elif not v: run = 0; start = None
        for k in range(1, len(pk)-1):
            if pk[k] > -36 and pk[k] - max(pk[k-1], pk[k+1]) > 10:
                clicks.append({"t": g0 + k/100, "db": float(pk[k])})
    stats_extra = {"pauses": len(pauses), "pause_total_s": round(sum(b-a for a, b in pauses), 1)}
    total = segs[-1]["end"] if segs else 1
    spoken = sum(r["dur"] for r in rows); allchars = sum(r["chars"] for r in rows)
    filler_total = sum(clean(r["text"]).count(f) for r in rows for f in FILLERS[:3])
    gaps = [r["gap"] for r in rows[:-1] if not r["in_cut"]]
    stats = {"total_s": round(total, 1), "spoken_s": round(spoken, 1), "chars": allchars, "cps_mean": round(allchars/spoken, 2),
             "cps_max": round(max(r["cps"] for r in rows), 2), "cps_min": round(min(r["cps"] for r in rows if r["chars"] > 3), 2),
             "gap_median": round(float(np.median(gaps)), 2), "gap_p90": round(float(np.percentile(gaps, 90)), 2), "gaps_over_1s": sum(g > 1.0 for g in gaps),
             "gaps_under_0.15": sum(g < 0.15 for g in gaps), "breaths": len(breaths), "breaths_in_clause": sum(b["in_clause"] for b in breaths),
             "clicks": len(clicks), "clicks_per_min": round(len(clicks) / (total/60), 1), "fillers_umuh": filler_total,
             "filler_starts": sum(bool(r["filler_start"]) for r in rows), "retake_spans": len(cut_spans),
             "tail_drop_mean_db": round(float(np.mean([r["tail_drop_db"] for r in rows])), 1), **stats_extra}
    json.dump({"stats": stats, "rows": rows, "breaths": breaths, "clicks": clicks, "cuts": cut_spans}, open(W/"speech.json", "w"), ensure_ascii=False, indent=1)
    # audio for the report
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", W/"audio16k.wav", "-b:a", "64k", W/"speech-audio.mp3"])
    notes = (P["dir"]/"speech-notes.md").read_text() if (P["dir"]/"speech-notes.md").exists() else "_（教练点评待写：运行 speech-coach skill）_"
    def pb(t): return f'<button class="pb" data-t="{t:.2f}">▶ {int(t//60)}:{t%60:04.1f}</button>'
    def cls(r):
        if r["in_cut"]: return "cut"
        if r["cps"] > 6.5: return "fast"
        if r["cps"] < 3.5 and r["chars"] > 3: return "slow"
        return ""
    tr = "".join(f'<tr class="{cls(r)}"><td>{pb(r["s"])}</td><td>{html.escape(r["text"])}</td><td>{r["chars"]}</td><td>{r["dur"]:.1f}</td>'
                 f'<td>{r["cps"]:.1f}</td><td>{r["gap"]:.2f}</td><td>{r["tail_drop_db"]:+.1f}</td><td>{"".join(r["filler_start"])}</td><td>{"重录段" if r["in_cut"] else ""}</td></tr>' for r in rows)
    br = "".join(f'<li>{pb(b["t"])} {b["d"]*1000:.0f} ms, {b["db"]:.0f} dB {"<b>（句中换气）</b>" if b["in_clause"] else ""}</li>' for b in breaths)
    ck = "".join(f'<li>{pb(c["t"])} {c["db"]:.0f} dB</li>' for c in clicks)
    st = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in stats.items())
    md = html.escape(notes).replace("\n", "<br>")
    doc = f"""<!doctype html><meta charset="utf-8"><title>口播分析 · {P['slug']}</title>
<style>body{{font:15px/1.5 -apple-system,"PingFang SC",sans-serif;max-width:1100px;margin:30px auto;padding:0 16px;color:#111}}
table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{border:1px solid #ddd;padding:4px 6px;text-align:left}}th{{background:#f5c518}}
tr.fast td{{background:#ffe9e9}}tr.slow td{{background:#e9f0ff}}tr.cut td{{color:#999;text-decoration:line-through}}
.pb{{font:12px monospace;background:#111;color:#f5c518;border:0;border-radius:4px;padding:2px 6px;cursor:pointer}}
audio{{position:sticky;top:0;width:100%;background:#fff;z-index:9}}.notes{{background:#fffbe6;border-left:6px solid #f5c518;padding:12px 16px}}
h2{{margin-top:34px}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}</style>
<h1>口播分析 · {P['slug']}</h1><audio id="a" controls src="speech-audio.mp3"></audio>
<p>方法：本地 whisper 词级时间戳 + 10 ms 帧能量/过零率启发式。<b>换气、咂嘴为疑似检测</b>（点按钮听原声核对）。红行 = 偏快（&gt;6.5 字/秒），蓝行 = 偏慢（&lt;3.5），删除线 = 已剪掉的重录段。</p>
<h2>教练点评</h2><div class="notes">{md}</div>
<div class="two"><div><h2>总体数据</h2><table>{st}</table></div>
<div><h2>疑似换气点（{len(breaths)}，句中 {stats['breaths_in_clause']}）</h2><ul>{br}</ul><h2>疑似咂嘴/口水音（{len(clicks)}）</h2><ul>{ck}</ul></div></div>
<h2>逐句</h2><table><tr><th>播放</th><th>句子</th><th>字</th><th>秒</th><th>字/秒</th><th>到下句间隔 s</th><th>句尾能量 dB</th><th>开头虚词</th><th></th></tr>{tr}</table>
<script>document.querySelectorAll('.pb').forEach(b=>b.onclick=()=>{{const a=document.getElementById('a');a.currentTime=+b.dataset.t-0.3;a.play()}})</script>"""
    (W/"speech-report.html").write_text(doc, encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1)); print("OK:", W/"speech-report.html")
if __name__ == "__main__": main()
