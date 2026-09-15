#!/usr/bin/env python3
"""Step 4: plan.json + cards + sfx + bgm -> output/<slug>.<aspect>.<lang>.mp4
Pass 1 (once per project): cut the 4K source on the keep list, alternate punch-in per jump cut,
                          emit 16:9 and 9:16 intermediates.
Pass 2 (per aspect x lang): subtitles/pops (.ass), PiP cards, outro, voice loudnorm + bgm + sfx."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.common import load_project, read_json, write_json, sh, ROOT, die
from lib import ass as ASS

def pass1(P, plan, prof):
    inter = P["work"]/"intermediate"; inter.mkdir(exist_ok=True)
    outs = {"16x9": inter/"cut.16x9.mov", "9x16": inter/"cut.9x16.mov"}
    if all(o.exists() for o in outs.values()) and "--force" not in sys.argv: print("  pass1: cached"); return outs
    edit = read_json(P["edit"]) if P["edit"] else {}
    keeps = plan["keeps"]; punch = edit.get("punch_in", [1.0, 1.12])
    r = sh(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0",P["source"]], quiet=True)
    SW, SH = map(int, r.stdout.strip().split(","))
    # 9:16 crop window in source pixels (face centred; override with edit.json crop_x_ratio)
    cw = int(SH * 9 / 16) // 2 * 2; cx = int((SW - cw) * edit.get("crop_x_ratio", 0.5)) // 2 * 2
    f, vl, vp, al = [], [], [], []
    for i, (a, b, sp) in enumerate(keeps):
        z = punch[i % len(punch)]
        vsp = f",setpts=PTS/{sp}" if sp != 1.0 else ""; asp = f",atempo={sp}" if sp != 1.0 else ""
        w, h = int(SW / z) // 2 * 2, int(SH / z) // 2 * 2; x, y = (SW - w) // 2, (SH - h) // 2
        f.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS{vsp},split=2[v{i}a][v{i}b]")
        f.append(f"[v{i}a]crop={w}:{h}:{x}:{y},scale=1920:1080:flags=lanczos[l{i}]")
        pw, ph = int(cw / z) // 2 * 2, h; px = cx + (cw - pw) // 2
        f.append(f"[v{i}b]crop={pw}:{ph}:{px}:{y},scale=1080:1920:flags=lanczos[p{i}]")
        f.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS{asp}[a{i}]")
        vl.append(f"[l{i}]"); vp.append(f"[p{i}]"); al.append(f"[a{i}]")
    n = len(keeps)
    f.append("".join(vl) + f"concat=n={n}:v=1:a=0[vl]")
    f.append("".join(vp) + f"concat=n={n}:v=1:a=0[vp]")
    f.append("".join(al) + f"concat=n={n}:v=0:a=1,asplit=2[a1][a2]")
    sh(["ffmpeg","-v","error","-y","-hwaccel","videotoolbox","-i",P["source"],"-filter_complex",";".join(f),
        "-map","[vl]","-map","[a1]","-c:v","h264_videotoolbox","-b:v","20M","-pix_fmt","yuv420p","-c:a","pcm_s16le",outs["16x9"],
        "-map","[vp]","-map","[a2]","-c:v","h264_videotoolbox","-b:v","20M","-pix_fmt","yuv420p","-c:a","pcm_s16le",outs["9x16"]])
    return outs

def pass2(P, plan, prof, inter, aspect, lang, cues_text):
    W, H = (1920, 1080) if aspect == "16x9" else (1080, 1920)
    out = P["output"]/f"{P['slug']}.{aspect}.{lang}.mp4"; P["output"].mkdir(exist_ok=True)
    asspath = P["work"]/f"subs.{aspect}.{lang}.ass"
    asspath.write_text(ASS.build(plan, prof, lang, aspect, cues_text), encoding="utf-8")
    D = plan["out_duration"]; OD = prof["outro"]["duration_s"]; T = D + OD
    au = prof["audio"]; ins = prof["inserts"]
    inputs = ["-i", inter[aspect], "-stream_loop", "-1", "-i", ROOT/au["bgm"]]
    f, vlab, amix = [], "[0:v]", []
    f.append(f"[0:v]tpad=stop_mode=clone:stop_duration={OD}[v0]"); vlab = "[v0]"
    idx = 2
    # sfx events: pops (+their sfx), inserts (whoosh), explicit sfx, outro ding
    events = []
    for p in plan["pops"]: events.append((p["s"], p.get("sfx", prof["keyword_pop"]["sfx"])))
    for i in plan["inserts"]: events.append((i["s"], ins["sfx_in"]))
    for x in plan["sfx"]: events.append((x["s"], x["name"]))
    events.append((D + 0.1, prof["outro"]["sfx"]))
    bleeps = [(x["s"], x["e"]) for x in plan["sfx"] if x["name"] == "bleep"]
    for t, name in events:
        inputs += ["-i", ROOT/"assets/sfx"/f"{name}.wav"]
        f.append(f"[{idx}:a]adelay={int(t*1000)}:all=1,volume={au['sfx_db']}dB[s{idx}]"); amix.append(f"[s{idx}]"); idx += 1
    # PiP cards
    pw = int(W * (ins["pip_width_ratio"] if aspect == "16x9" else ins.get("pip_width_ratio_9x16", 0.62))); m = ins["pip_margin"]; fd = ins["fade_s"]
    for k, i in enumerate(plan["inserts"]):
        png = P["work"]/"cards"/f"{i['card']}.{lang}.png"; hold = i["e"] - i["s"]
        inputs += ["-loop", "1", "-t", f"{hold:.3f}", "-i", png]
        x, y = (W - pw - m, 120) if aspect == "16x9" else (W - pw - m, 110)
        f.append(f"[{idx}:v]scale={pw}:-1,format=rgba,fade=t=in:st=0:d={fd}:alpha=1,fade=t=out:st={hold-fd:.3f}:d={fd}:alpha=1,setpts=PTS+{i['s']}/TB[c{k}]")
        f.append(f"{vlab}[c{k}]overlay={x}:{y}:eof_action=pass[v{k+1}]"); vlab = f"[v{k+1}]"; idx += 1
    # outro
    inputs += ["-loop", "1", "-t", f"{OD}", "-i", P["work"]/"cards"/f"outro.{aspect}.{lang}.png"]
    f.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.5:alpha=1,setpts=PTS+{D}/TB[oc]")
    f.append(f"{vlab}[oc]overlay=0:0:eof_action=pass[vo]"); idx += 1
    f.append(f"[vo]ass={asspath}:fontsdir={ROOT/prof['brand']['fonts_dir']},format=yuv420p[vout]")
    # audio
    vf = f"[0:a]loudnorm={au['voice_loudnorm']}"
    for s, e in bleeps: vf += f",volume=enable='between(t,{s},{e})':volume=0"
    f.append(vf + f",apad=pad_dur={OD}[voice]")
    f.append(f"[1:a]atrim=0:{T},asetpts=PTS-STARTPTS,volume={au['bgm_db']}dB,afade=t=in:d={au['bgm_fade_s']},afade=t=out:st={T-au['bgm_fade_s']-0.5}:d={au['bgm_fade_s']}[bgm]")
    f.append(f"[voice][bgm]{''.join(amix)}amix=inputs={2+len(amix)}:normalize=0:duration=first[aout]")
    sh(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(f),"-map","[vout]","-map","[aout]",
        "-c:v","h264_videotoolbox","-b:v","12M","-profile:v","high","-c:a","aac","-b:a","192k","-ar","48000",
        "-movflags","+faststart","-t",f"{T:.3f}",out])
    return out

def main():
    P = load_project(sys.argv[1]); prof = P["profile"]; plan = read_json(P["work"]/"plan.json")
    edit = read_json(P["edit"]) if P["edit"] else {}
    plan["title"] = edit.get("title", {}); plan["subtitle"] = edit.get("subtitle", {})
    cues_text = {}
    if (P["dir"]/"cues.en.json").exists():
        cues_text = {k: v for k, v in read_json(P["dir"]/"cues.en.json").items() if not k.startswith("$")}
    want = [a for a in sys.argv[2:] if a in ("16x9", "9x16")] or ["16x9", "9x16"]
    langs = [a for a in sys.argv[2:] if a in ("zh", "en")] or prof["creator"]["languages"]
    inter = pass1(P, plan, prof)
    outs = []
    for aspect in want:
        for lang in langs:
            if lang == "en" and not cues_text: print("skip en: no cues.en.json"); continue
            outs.append(pass2(P, plan, prof, inter, aspect, lang, cues_text))
    missing = [k for k in plan["cues"]["zh"] if not k.get("skipped") and langs.count("en") and k["text"] not in cues_text]
    if missing: print(f"WARN: {len(missing)} zh cues have no en translation (shown in zh): {[m['text'] for m in missing][:5]}")
    print("OK:", *[str(o) for o in outs], sep="\n  ")
if __name__ == "__main__": main()
