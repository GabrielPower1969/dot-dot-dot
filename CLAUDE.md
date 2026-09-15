# dot-dot-dot — map for agents

One recording + one script → cut, subtitled, branded videos (16:9 + 9:16, zh + en) + covers + copy for every platform.
Design: `docs/ARCHITECTURE.md`. How to work with it: `docs/PLAYBOOK.md`. Users: `README.md`.

## Commands
```bash
python3 src/build.py projects/<slug>          # THE command: 1 transcribe → 2 plan → 2b translate → 3 cards → 4 assemble → 5 package
npm run plan     projects/<slug>              # any single step: transcribe | plan | cards | assemble | package
python3 src/steps/4-assemble.py projects/<slug> 9x16 zh   # one aspect / one language
python3 src/ui/server.py 7777                 # local studio UI (blueprint editor, runs the same steps, writes the same files) → http://localhost:7777
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
config/profile.json    personal style (locked): brand.theme (→ themes.json), display fonts, cut rules, subtitle sizes, pop style, PiP, audio levels, outro, rules[]
config/themes.json     colour systems (editorial: ink-classic, indigo-porcelain, forest-ink, kraft-paper, dune, midnight-ink · swiss: ikb-blue, lemon-green, safety-orange). Palettes adapted from guizang-social-card-skill. NO yellow/black sticker look.
assets/fonts/fonts.json the only font registry (all OFL). scripts/fetch-fonts.sh downloads the big ones. Cover variants reference fonts by id.
config/platforms.json  per-platform aspect, sizes, limits, owner, where to publish, verified date
config/llm.json        providers (anthropic + every OpenAI-compatible) · tiers desktop/api_expensive/api_cheap · routes task→providers · budget
assets/                fonts/ brand/ sfx/ music/ broll/ + manifest.json (licence per file)
templates/cards/       PiP cards & outro, editorial system (_base.css imports generated _theme.css)   templates/covers/cover.html  styles: editorial | swiss | photo | outline   templates/copy/ post.md
src/lib/theme.py|js    profile.brand.theme → tokens; writes templates/cards/_theme.css before every render; ASS pops/lower-third/outro use the same tokens
src/steps/1..5         the pipeline (python: 1,2,2b,4 · node: 3,5)   src/lib/  common, timeline (cuts+speed↔output time), ass (subtitle builder)
src/llm/router.py      call(task, prompt): route → provider chain, disk cache, usage log
src/publish/           queue + browser adapters (design + stubs)     src/monitor/  metrics pull + digest (design + stubs)
src/ui/server.py       stdlib HTTP: /api/projects /api/project/<slug> /api/file (GET/PUT, whitelisted) /api/run (spawns a step) /api/assets /api/queue /api/inbox /media/* (Range)
src/ui/index.html      single-page studio: 项目 · 蓝图(node graph) · 剪辑(timeline+player) · 成片 · 封面选型(contact sheet → pick frame/title/font/style → variants + 120px strip) · 文案 · 口播 · 交接&发布 · 队列 · 数据 · 任务箱 · 设置
ui/inbox.jsonl         requests typed in the UI for the agent (status open → done)
.claude/skills/        video-edit · video-package · cover-design (frame/title/font/style are the CREATOR's choice; variants + 120px strip; routes 小红书/公众号 to guizang-social-card-skill in ~/.claude/skills, AGPL, not vendored) · video-publish · speech-coach · trend-radar · sponsor-inbox
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
- **Design system:** one theme per video from `config/themes.json`; accent used once per frame; editorial type is regular weight + wide tracking; never the yellow/black sticker look. Fonts only from `fonts.json`.
- **Covers are chosen by the creator.** `copy.<lang>.cover` = {frame_s, kicker, title_html, variants[{font,style,size}], pick}. Step 5 renders every variant (`.vN.png`) + `legibility-<lang>.png`; the pick is copied to the unsuffixed name.
- **UI holds no state.** Human edits in the studio UI and agent edits from the CLI touch the same files; never cache project state elsewhere.

## Verify a change
1. `python3 src/build.py projects/2026-09-15-tangping` ends with `DONE` and no `WARN: anchor`.
2. Step 2 prints exactly 2 cuts for the sample (the 60 s retake + the manual stumble) and coverage ≥ 85 %.
3. Look at 4 frames per output (pop, PiP, corner, outro) — a montage: `magick montage ...`. Subtitles must not be ASR text.
4. Cards/covers: `npm run cards` / `npm run package`, open the PNGs.
