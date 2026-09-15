# Playbook — how to work with dot-dot-dot (and how to think about the agent architecture)

## A normal week

| Day | You | Agent / code |
|---|---|---|
| Mon | read `ideas/<date>.md` (trend radar), pick one, write `script.md` | `trend-radar` ran overnight on the cheap tier |
| Tue | record; save as `projects/<date>-<topic>/source/raw.mp4`; paste what you actually said into `voiceover.md` | — |
| Tue | tell the desktop agent "edit this" | `video-edit` skill → `edit.json`; `python3 src/build.py` → 4 videos, 10 covers, 12 posts |
| Tue | watch the 16:9 zh cut; change 2–3 lines in `edit.json` if needed; re-run step 4 | `speech-coach` report tells you where the breaths and pace slipped |
| Wed | say "publish 小红书 + 抖音 tonight, rest tomorrow 19:00" | `video-publish` fills the studio pages, shows screenshots, waits for your yes per platform |
| Fri | read the weekly digest; reply to 3 comments; answer 1 sponsor | monitor pulls numbers; `sponsor-inbox` drafted the reply |

Total human time per video: writing + recording + ~20 minutes of review.

## Harness agent vs graph orchestration — which fits you

You asked what technology fits your background (engineer, one-person creator, strong taste, Mac, Claude Code user).

| | **Harness / skill agent** (what this repo is) | **Graph orchestration** (LangGraph, AutoGen, n8n, Airflow) |
|---|---|---|
| Shape | deterministic pipeline in code; the agent fills in *judgement JSON* and drives the browser | a graph of LLM nodes with state passed between them |
| Where taste lives | `config/profile.json` + `edit.json`, read by a human | inside prompts and node code |
| Debugging | diff a JSON, re-run one step | replay a graph run, inspect state |
| Cost | tokens only where judgement is needed | tokens on every node, every run |
| When it wins | one operator, high style consistency, outputs must be reviewable | many operators, many branching workflows, need a visual editor for non-engineers |

**Recommendation: stay harness-first for 12 months.** Reasons: (1) you review everything anyway, and JSON is the
cheapest thing to review; (2) 90 % of the work (ffmpeg, Playwright, alignment) is deterministic and *should not* be an
LLM node; (3) you already live in Claude Code — skills are free, graphs are a second product to maintain.
Add a graph engine only when a *second person* needs to change the workflow without reading code, and then prefer
n8n (self-hosted, visual, can call these steps as shell nodes) over rewriting in LangGraph. Do not put Celery, Redis or
Kubernetes anywhere near this until you have a team.

## Token plan

- **Desktop subscription** pays for taste: edit plans, reviews, publish sessions. Keep prompts to script + plan
  summary, never raw transcript JSON. Frames are inspected as small montages, not per-frame.
- **Expensive API** (`anthropic`, `openai`) only for unattended batches: nightly edit plans for a backlog, English copy.
- **Cheap API / local** (`deepseek`, `zhipu`, `doubao`, `ollama`) for everything mechanical: translation (≈ 60 lines
  per video ≈ 2k tokens), summaries, tagging, monitoring digests. Route table in `config/llm.json`; change a route, not code.
- Cache is on by default (`.cache/llm/`) — re-running a step never re-pays for the same prompt.
- Memory is *files*: `memory/*.md` with rules you taught the agent ("no piano beds", "always subtitle numbers as digits").
  A vector DB is unnecessary below ~500 videos; grep is faster and inspectable.

## The three files you will actually touch

1. `voiceover.md` — paste what you said. If coverage in step 2 drops below 85 %, this file is wrong, not the code.
2. `edit.json` — anchors are quotes. Add a pop: `{"anchor":"温水煮青蛙","text":{"zh":"温水煮青蛙","en":"Boiling the frog"}}`.
   Cut a stumble: `{"from_s":124.5,"to_s":126.0,"why":"..."}`. Slow-mo: `"speed":[{"from_s":40,"to_s":42,"factor":0.5}]`.
3. `copy.json` — titles per platform, hook, hashtags, `cover_time_s` (pick the frame where you smile).

## What to do when

- Subtitles show ASR-looking text → the cue was `skipped` (not matched); fix `voiceover.md`.
- A retake was not cut → add `manual_cuts`. A good take was cut → lower nothing; add `"keep": true`... (planned) or split the segment in `manual_cuts` with `why`.
- PiP covers your face → change `inserts.pip_width_ratio*` in profile (global) or move the anchor to a line where you lean the other way.
- The English pop is too wide → shorten the en text; pops are one to three words.
