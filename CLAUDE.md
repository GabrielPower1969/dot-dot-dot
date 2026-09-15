# dot-dot-dot — map for agents

One recording + one script → cut, subtitled, branded videos (16:9 + 9:16, zh + en) + covers + copy for every platform.
Design: `docs/ARCHITECTURE.md`. How to work with it: `docs/PLAYBOOK.md`. Users: `README.md`.

## Commands
```bash
python3 src/build.py projects/<slug>          # THE command: 1 transcribe → 2 plan → 2b translate → 3 cards → 4 assemble → 5 package
npm run plan     projects/<slug>              # any single step: transcribe | plan | cards | assemble | package
python3 src/steps/4-assemble.py projects/<slug> 9x16 zh   # one aspect / one language
```
Setup once: `brew install ffmpeg`, `npm install` (Playwright), `scripts/make-sfx.sh` (placeholder SFX/bed), a Python with `mlx-whisper` (`python3 -m venv .venv && .venv/bin/pip install mlx-whisper`).

## Where things are (folder order = data flow)
```
projects/<slug>/       INPUT+OUTPUT per video. slug = <yyyy-mm-dd>-<topic>.
  script.md            the written article (author's text)
  voiceover.md         what was actually read on camera (script + outro). Subtitles come from THIS, not from ASR.
  edit.json            per-video judgement: title, manual_cuts, pops, inserts, sfx, speed, outro. WHERE = a quote from voiceover.md.
  copy.json            per-platform titles/hook/body/hashtags, cover_time_s, publish_order
  cues.en.json         zh subtitle line → en line (LLM 'translate' route or by hand)
  source/*.mp4         raw recording (git-ignored)
  work/                transcript.json (words) · plan.json (resolved times) · cards/*.png · subs.*.ass · intermediate/cut.*.mov
  output/              <slug>.<16x9|9x16>.<zh|en>.mp4 · covers/<platform>.<lang>.<WxH>.png · <platform>/<platform>-post-<topic>-<date>.<lang>.md · README.md
config/profile.json    personal style (locked): fonts, colours, cut rules, subtitle sizes, pop style, PiP, audio levels, outro, rules[]
config/platforms.json  per-platform aspect, sizes, limits, owner, where to publish, verified date
config/llm.json        providers (anthropic + every OpenAI-compatible) · tiers desktop/api_expensive/api_cheap · routes task→providers · budget
assets/                fonts/ brand/ sfx/ music/ broll/ + manifest.json (licence per file)
templates/cards/       PiP cards & outro (HTML → PNG via Playwright, offline)   templates/covers/  cover.html   templates/copy/ post.md
src/steps/1..5         the pipeline (python: 1,2,2b,4 · node: 3,5)   src/lib/  common, timeline (cuts+speed↔output time), ass (subtitle builder)
src/llm/router.py      call(task, prompt): route → provider chain, disk cache, usage log
src/publish/           queue + browser adapters (design + stubs)     src/monitor/  metrics pull + digest (design + stubs)
.claude/skills/        video-edit (script+recording → edit.json) · video-package (copy.json) · video-publish · speech-coach · trend-radar · sponsor-inbox
```

## Invariants (do not break)
- **Offline render.** ffmpeg + libass + Playwright on `file://` only. Audio never leaves the machine (mlx-whisper local).
- **Subtitles = voiceover.md text**, aligned to ASR by character diff. Never ship ASR text as subtitles.
- **Retake rule:** keep the LAST take; cut from the first false start to the restart. Detected in step 2, overridable in `edit.json.manual_cuts`.
- **zh and en share one cut.** Only subtitles, pops, cards, outro and cover text differ. Times live once, in `work/plan.json`.
- **Style is config, judgement is edit.json.** Never change `config/profile.json` or a template for one video.
- **Anchors are quotes.** `edit.json` says *where* with text from the script, never with seconds (except `manual_cuts`, `speed`, `at_s` fallbacks).
- **Slug format enforced; one source file per project.**
- **Assets need a licence line in `assets/manifest.json`** before they are used in a render.
- Fixed process = code, judgement = skill. Don't re-derive ffmpeg graphs in prompts.

## Verify a change
1. `python3 src/build.py projects/2026-09-15-tangping` ends with `DONE` and no `WARN: anchor`.
2. Step 2 prints exactly 2 cuts for the sample (the 60 s retake + the manual stumble) and coverage ≥ 85 %.
3. Look at 4 frames per output (pop, PiP, corner, outro) — a montage: `magick montage ...`. Subtitles must not be ASR text.
4. Cards/covers: `npm run cards` / `npm run package`, open the PNGs.
