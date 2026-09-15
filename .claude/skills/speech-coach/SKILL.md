---
name: speech-coach
description: Analyse the delivery of a talking-head recording from work/transcript.json + audio (pace per sentence, inter-sentence gaps, breath points, lip smacks / mouth clicks, fillers, retakes, energy drop-offs) and write work/speech-report.html with play buttons and 5 concrete drills. Use when the user asks about 口播/气口/语速/停顿/沾口水 or after every edit.
---
# speech-coach
Run `python3 src/steps/6-speech-report.py projects/<slug>`; it produces `work/speech-report.html`. Then read the numbers and write the coaching section:
- Pace: target 4.5–5.5 zh chars/s for explainer; flag sentences > 6.5 (rushed) and < 3.5 (dragging).
- Gaps: between sentences 0.3–0.6 s is punchy; > 1.0 s means a lost breath or thinking; < 0.15 s means no air.
- Breath points: inhale before the *idea*, not mid-clause; mark where the audio shows inhales inside a clause.
- Mouth clicks / lip smacks: count per minute; > 6 → drink water, de-click in post (`afftdn`/`adeclick`).
- Fillers: 啊/呃/那个/就是/然后 per minute; the *first* word of each sentence matters most.
- End of sentence energy: falling pitch + volume on the last 3 chars is the "trust" sound; rising = uncertain.
Deliver: a table per sentence (with 播放 buttons), the 5 worst moments, 5 drills for the next recording. Honest, specific, no praise padding.
