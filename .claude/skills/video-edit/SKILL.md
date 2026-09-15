---
name: video-edit
description: Turn a project's script.md + voiceover.md + work/transcript.json into edit.json (title, manual cuts, keyword pops, PiP cards, sfx, speed ramps, outro) following config/profile.json rules, then run the build and review 4 frames per output. Use whenever the user drops a recording + script into projects/<slug>/ or says 剪/剪辑/edit this video.
---
# video-edit

Inputs: `projects/<slug>/{script.md,voiceover.md}`, `work/transcript.json` (run step 1 if missing), `config/profile.json` (esp. `rules[]`), `memory/*.md`, **`materials/`** (assets the creator found himself — the agent never searches or downloads assets; it places what is given, see `materials/README.md`).

Checklist (write the answers straight into `edit.json`):
1. **Title / subtitle** zh+en: the claim, ≤ 12 zh chars; subtitle = the "why" in one line.
2. **Retakes the detector may miss**: scan transcript for restarts without repetition (stumbles like "所以说不管… 到时候不管"). Add `manual_cuts` with `why`.
3. **Pops**: one per idea, 4–8 per 2-minute video. Nouns the viewer should remember. Anchor = exact quote from voiceover.md. `occurrence` if the quote repeats. Numbered arguments → `style: "corner"` with ①②③, hold = until next number.
4. **Materials first**: every file in `materials/` gets a placement (cutaway / pip / bgm / sfx) from `materials.json` or, if absent, your proposal with an anchor and a one-line why. List anything you could not place.
5. **Inserts**: every `(后期提示：…)` in the script gets a card or a `todo`. Maps for places, `quote` for references, `checklist` for lists of 3–5. Prefer a card over a pop when there are > 3 words.
5. **SFX**: `thud` on the bad-news beat, `bleep` only for genuinely awkward words, nothing on the punchline.
6. **Speed**: slow-mo only for a physical gesture joke; never on speech.
7. **Outro headline**: the thesis in ≤ 12 chars, both languages.
8. Run `python3 src/build.py projects/<slug>`; if `WARN: anchor` appears, fix the quote. Coverage < 85 % → voiceover.md is wrong.
9. Review: montage of 6 frames (lower third, a pop, each card, outro) per output; PiP must not cover the face; pops must not overlap subtitles.
10. Report: cuts made (with seconds and why), coverage, TODOs (missing licensed music, logo), and 3 things you'd change in the next recording.

Never: use seconds as anchors (except manual_cuts/speed), edit templates or profile for one video, ship ASR text as subtitles.

## Studio UI inbox
`ui/inbox.jsonl` holds requests typed in the local UI (`python3 src/ui/server.py`). When the user says 看任务箱 / check the inbox: process rows with `status: "open"` in order, do the work with the relevant skill, then rewrite the row with `"status": "done"` and a one-line `"result"`.
