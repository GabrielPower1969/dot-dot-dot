# Architecture — the film pipeline, run by agents

Think of it as a one-person film studio where every department is either **code** (deterministic, testable) or a
**skill** (judgement, done by an agent that reads your rules). Stages are numbered; data flows left to right through
`projects/<slug>/`.

| # | Studio department | Stage | Code | Judgement (skill) | Artefact |
|---|---|---|---|---|---|
| 0 | Development | **Trend radar** | `src/monitor/trends.py` (stub) | `trend-radar` | `ideas/<date>.md` — hooks worth recording |
| 1 | Writers' room | **Script** | — | you (+ `speech-coach` for delivery notes) | `script.md`, `voiceover.md` |
| 2 | Set | **Record** | — | you | `source/raw.mp4` (4K, 30 fps, room mic) |
| 3 | Cutting room | **Transcribe + plan** | steps 1–2 | `video-edit` writes `edit.json` | `work/transcript.json`, `work/plan.json` |
| 4 | Art department | **Cards, looks, stickers** | step 3 | `video-edit` picks cards/vars | `work/cards/*.png` |
| 5 | Sound stage | **Assemble** | step 4 | levels & sfx choices from `profile.json` | `output/*.mp4` |
| 6 | Marketing | **Package** | step 5 | `video-package` writes `copy.json` | covers, posts, hand-off README |
| 7 | Distribution | **Publish** | `src/publish/queue.py` + adapters | `video-publish` (drives the browser, asks before the final click) | `publish/queue.json`, receipts |
| 8 | Box office | **Monitor** | `src/monitor/pull.py` | `monitor_digest` (cheap LLM) | `metrics/<slug>.jsonl`, weekly digest |
| 9 | Sponsors | **Deals inbox** | Gmail MCP | `sponsor-inbox` | `deals/<brand>.md`, draft replies (never sent without you) |

## Data model (all plain files, all diffable)

```
config/profile.json      you        locked style, cut rules, audio levels, outro, rules[]
config/platforms.json    world      per-platform specs (verified date per row)
config/llm.json          money      providers, tiers, routes, budget
projects/<slug>/
  script.md · voiceover.md · edit.json · copy.json · cues.en.json     ← human/agent-authored, small, reviewable
  work/transcript.json → plan.json → cards/ → subs.*.ass → intermediate/ ← generated, disposable
  output/                                                              ← deliverables
memory/                  (planned) rules you taught the agent: "no piano bgm", "always 差不多 joke card" — markdown, grep-able
```

### plan.json is the contract
Step 2 resolves every anchor to `src_s/src_e` (source) **and** `s/e` (output) using `lib/timeline.py`
(keeps with speed factors → cumulative offsets). Steps 3–5 only read `plan.json`. A new aspect, language or renderer
never touches alignment logic.

### Alignment
`difflib.SequenceMatcher` over *characters* between ASR text and the cleaned script. Matched chars get the ASR word's
time (interpolated inside a word); unmatched script chars are interpolated between neighbours; a cue with < 30 %
matched chars is marked `skipped` (you didn't say it). Coverage < 80 % means the voiceover file doesn't reflect the
take — fix the file, not the code.

### Retakes
Segment i is a false start of segment j (within 15 s) when the first phrases are ≥ 0.6 similar **and** the whole run
[i, j) is ≥ 0.6 similar to what follows j. This rejects "第一个…/第二个…" list patterns. Result: cut [i.start, j.start).

## Video language (what "personal style" means in code)

| Element | Where defined | Implementation |
|---|---|---|
| Jump cuts + alternating punch-in (1.0× / 1.12×) | `profile.cut`, `edit.punch_in` | crop on the 4K source per keep segment → lossless at 1080p |
| Speed ramps (slow-mo / fast) | `edit.speed[{from_s,to_s,factor}]` | `setpts` + `atempo` per split segment; timeline aware |
| Subtitles with keyword highlight | `profile.subtitles` | libass; `Sub` style; pop words coloured inline |
| Keyword pops (大字) | `profile.keyword_pop`, `edit.pops` | ASS `\t` scale bounce, `\frz-4`, right of face (16:9) / top (9:16) + `pop.wav` |
| Corner counters ①②③ | `edit.pops[style=corner]` | ASS `Corner` style, top-left |
| Lower third title | `edit.title/subtitle` | ASS `\move` slide-in, 3.2 s |
| PiP cards (map, quote, checklist) | `templates/cards/*.html`, `edit.inserts` | Playwright PNG → ffmpeg overlay with alpha fades + `whoosh.wav` |
| Outro | `templates/cards/outro.html` | last frame frozen 4 s under an opaque card + `ding.wav` |
| Bleep | `edit.sfx[name=bleep]` | voice muted for the span + 1 kHz tone |
| Bed music | `profile.audio.bgm` at −30 dB | loop, fade in/out |
| Voice | `loudnorm I=-16 TP=-1.5` | broadcast-safe for every platform |
| Looks / transitions per scene (planned) | `edit.looks[{anchor,look}]` | ffmpeg `curves`/`lut3d` presets: `memory` (warm, vignette, 12 fps), `news`, `dream`; whip-pan `xfade` between scenes only, never inside talking head |
| Expression stickers (planned) | `edit.stickers[{anchor,sticker}]` | PNG pack (blush, big-eyes, shock, sweat) anchored to face box from step 1b (mediapipe) |
| Auto-reframe for 9:16 (planned) | step 1b | per-second face centre → smooth `crop` expression instead of fixed centre |
| **Clip library** (planned v0.2) | `assets/library/catalog.json`, `edit.json.inserts[card=clip]` | reusable shots of *you* (reaction faces, intro/outro takes, hand gestures, "wait what" turns) and licensed B-roll, tagged by mood/keyword; step 4 cuts them in as full-frame cutaways with the voice continuing, or as PiP; every clip has a licence row and a poster frame |
| B-roll & AI scenes (planned) | `assets/broll/`, `edit.inserts[card=broll]` | licensed clips or generated stills (Ken Burns), never presented as real footage without a label |

## Agents and skills

Skills are Markdown in `.claude/skills/<name>/SKILL.md`. Each says: inputs, the checklist of judgement calls, the
JSON it must write, and what it must *not* do (no seconds as anchors, no template edits). The desktop agent
(Claude Code) runs them interactively; the same skills can run unattended via `src/llm/router.py` with the
`api_expensive` tier when you batch.

| Skill | Reads | Writes | Tier |
|---|---|---|---|
| `video-edit` | script, voiceover, transcript, profile.rules | `edit.json` | desktop / api_expensive |
| `video-package` | edit.json, platforms | `copy.json` | desktop / api_cheap for zh, expensive for en |
| `video-publish` | output/README.md, queue | browser actions, `publish/receipts.jsonl` | desktop only (needs your logged-in browser) |
| `speech-coach` | transcript words, audio stats | `work/speech-report.html` | code + desktop |
| `trend-radar` | RSS / platform trending pages | `ideas/<date>.md` | api_cheap |
| `sponsor-inbox` | Gmail (label `sponsor`) | `deals/*.md`, draft replies | desktop / api_expensive |

## LLM tiers and token discipline (`config/llm.json`)

- **desktop** — the agent you talk to (subscription). Taste, review, anything that needs to see the frames.
- **api_expensive** — Anthropic / OpenAI keys. Unattended edit plans, English copy, sponsor reply drafts.
- **api_cheap** — DeepSeek / Zhipu / Doubao / local Ollama. Translation, summaries, tagging, monitoring digests, zh copy.
- Every call goes through `router.call(task, prompt)`: route → provider chain with fallback, disk cache keyed by prompt,
  usage appended to `.cache/llm/usage.jsonl`. Hard cap `max_input_tokens_per_call`; the rule is *send the script and a
  cue index, never the raw word JSON*. Long histories are summarised into `memory/` markdown, not re-sent.

## Publishing (stage 7) — design

- **Browser, not APIs.** Douyin/小红书/快手/B站 have no creator upload API for individuals; YouTube/LinkedIn/Meta do but
  quota and review make them worse than the web studio for one person. So: Playwright with a *persistent profile*
  (`~/.dotdotdot/browser/<platform>`) that you log into once; the agent drives the same pages you would.
- **Queue file, not a scheduler service.** `publish/queue.json` rows `{slug, platform, lang, at, status}`; `queue.py run`
  is called by cron/launchd every 15 min. No Redis, no Celery — one creator, ten posts a week.
- **Two-step confirmation.** Adapters fill everything and stop at the final button unless the row has `"confirmed": true`
  set by you (or by the desktop agent after you said yes in chat). Credentials never enter prompts.
- Adapter interface: `prepare(row) → screenshot`, `submit(row) → receipt(url)`, `verify(url) → live?`.

## Monitoring (stage 8) — design

Per platform: pull views/likes/comments/saves at +1 h, +24 h, +7 d, +30 d (browser scrape of the creator dashboard,
API where it exists), append to `metrics/<slug>.jsonl`. Weekly digest by the cheap tier: what worked, hook retention,
best posting hour, comments worth replying to. Dashboard = one static HTML page generated from the jsonl (no server).

## Security

- Keys only from env; `.env` git-ignored; router never logs prompts containing `sk-`.
- Browser profiles live outside the repo; adapters refuse to run on a non-persistent context.
- Anything that leaves the machine (publish, reply, email) is a **confirm-first** action, logged with a receipt.
- Sponsor inbox: read + draft only. Sending is a human click.
- Media is never uploaded to any LLM. Frames the agent inspects are local PNGs.

## What is public vs private

Public (git): code, templates, configs, the sample project's JSON/markdown, synthesised SFX.
Private (ignored): `projects/*/source`, `output`, `work/intermediate`, real music, browser profiles, `.env`, `metrics/`, `deals/`.
