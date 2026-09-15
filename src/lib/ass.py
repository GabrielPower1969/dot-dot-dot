"""Build an .ass subtitle file (libass) from plan.json: subtitles, keyword pops, corner counters, lower third."""
def ts(t):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
def col(hexrgb, alpha="00"):  # "#RRGGBB" -> "&HAABBGGRR"
    r, g, b = hexrgb[1:3], hexrgb[3:5], hexrgb[5:7]; return f"&H{alpha}{b}{g}{r}"

def build(plan, prof, lang, aspect, cues_text):
    W, H = (1920, 1080) if aspect == "16x9" else (1080, 1920)
    sub, pop, br = prof["subtitles"], prof["keyword_pop"], prof["brand"]
    font = br["font_zh"] if lang == "zh" else br["font_en"]
    fs = sub[f"font_size_{aspect.replace('x',':') if False else aspect}"] if False else sub[f"font_size_{aspect}"]
    mv = sub[f"margin_v_{aspect}"]
    if lang == "en": fs = int(fs * 0.9)
    yellow, ink, white = col(br["primary"]), col(br["ink"]), "&H00FFFFFF"
    pop_fs = pop["font_size"] if aspect == "16x9" else int(pop["font_size"] * 0.85)
    if lang == "en": pop_fs = int(pop_fs * 0.72)
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{font},{fs},{white},{white},{ink},&H80000000,1,0,0,0,100,100,0,0,1,{sub['outline']},{sub['shadow']},2,60,60,{mv},1
Style: Pop,{font},{pop_fs},{yellow},{yellow},{ink},&H80000000,1,0,0,0,100,100,0,0,1,{pop['outline']},0,5,0,0,0,1
Style: Corner,{font},{int(pop_fs*0.9)},{yellow},{yellow},{ink},&H80000000,1,0,0,0,100,100,0,0,1,{pop['outline']},0,7,0,0,0,1
Style: LT1,{font},{78 if aspect=='16x9' else 66},{ink},{ink},{yellow},&H00000000,1,0,0,0,100,100,0,0,3,14,0,7,0,0,0,1
Style: LT2,{font},{40 if aspect=='16x9' else 36},{white},{white},{ink},&H80000000,1,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    # subtitles (+ keyword highlight)
    keywords = [p["text"][lang] for p in plan["pops"] if p.get("style") != "corner"]
    for c in plan["cues"][lang if lang in plan["cues"] else "zh"]:
        if c.get("skipped"): continue
        text = cues_text.get(c["text"], c["text"]) if lang != "zh" else c["text"]
        for k in keywords:
            if k and k in text: text = text.replace(k, f"{{\\c{yellow}}}{k}{{\\c{white}}}", 1)
        ev.append(f"Dialogue: 0,{ts(c['s'])},{ts(c['e'])},Sub,,0,0,0,,{text}")
    # pops
    b = pop["bounce_ms"]
    for p in plan["pops"]:
        txt = p["text"][lang]
        if p.get("style") == "corner":
            x, y = (70, 60) if aspect == "16x9" else (56, 250)
            ev.append(f"Dialogue: 2,{ts(p['s'])},{ts(p['e'])},Corner,,0,0,0,,{{\\pos({x},{y})\\fscx60\\fscy60\\t(0,{b},\\fscx108\\fscy108)\\t({b},{b+120},\\fscx100\\fscy100)\\fad(0,200)}}{txt}")
        else:
            x, y = (1440, 400) if aspect == "16x9" else (540, 430)
            ev.append(f"Dialogue: 2,{ts(p['s'])},{ts(p['e'])},Pop,,0,0,0,,{{\\pos({x},{y})\\frz-4\\fscx50\\fscy50\\t(0,{b},\\fscx112\\fscy112)\\t({b},{b+120},\\fscx100\\fscy100)\\fad(0,220)}}{txt}")
    # lower third (intro)
    if plan.get("intro") and plan["title"].get(lang):
        d = prof["intro"]["lower_third_s"]
        x, y1, y2 = (80, 90, 210) if aspect == "16x9" else (60, 300, 400)
        ev.append(f"Dialogue: 3,{ts(0.3)},{ts(0.3+d)},LT1,,0,0,0,,{{\\move({x-500},{y1},{x},{y1},0,320)\\fad(0,250)}}  {plan['title'][lang]}  ")
        if plan["subtitle"].get(lang):
            ev.append(f"Dialogue: 3,{ts(0.5)},{ts(0.3+d)},LT2,,0,0,0,,{{\\move({x-500},{y2},{x},{y2},0,320)\\fad(0,250)}}{plan['subtitle'][lang]}")
    return hdr + "\n".join(ev) + "\n"
