# dot-dot-dot

> *"You can't connect the dots looking forward; you can only connect them looking backwards."* — Steve Jobs, Stanford 2005

Every video you make is a dot. **dot-dot-dot** is the studio that connects them: one recording + one script in,
finished videos for every platform out — cut, subtitled, branded, in Chinese **and** English — plus covers, post copy,
a publish queue and the numbers that come back. Built for one creator with a strong personal style, run by an AI agent
that follows *your* rules, on *your* machine.

```
   script.md + recording.mp4
          │
   ┌──────▼──────┐   ┌──────────┐   ┌──────────┐   ┌───────────┐   ┌───────────┐   ┌──────────┐
   │ 1 transcribe│ → │ 2 plan   │ → │ 3 cards  │ → │ 4 assemble│ → │ 5 package │ → │ 6 publish│ → 7 monitor
   │ local ASR   │   │ cuts,    │   │ PiP maps,│   │ 16:9+9:16 │   │ covers ×10│   │ browser  │   views, comments,
   │ words+times │   │ align,   │   │ quotes,  │   │ zh + en   │   │ platforms │   │ queue    │   sponsor inbox
   └─────────────┘   │ anchors  │   │ outro    │   │ subs,pops,│   │ post copy │   └──────────┘
                     └──────────┘   └──────────┘   │ sfx, bgm  │   └───────────┘
                                                   └───────────┘
```

## What it does today (v0.1)

| Stage | Done by | What you get |
|---|---|---|
| **Transcribe** | mlx-whisper, on-device | word-level timestamps; audio never leaves your Mac |
| **Plan the cut** | code + agent | retakes removed automatically (keeps the last take), long pauses tightened, subtitles taken from *your script* (not ASR), keyword pops / picture-in-picture cards / SFX placed by quoting the script |
| **Cards** | HTML → PNG, offline | map, quote, checklist, outro; one template, two languages |
| **Assemble** | ffmpeg + libass | 16:9 and 9:16 from one 4K source (face-centred crop, alternating punch-in on every jump cut, speed ramps), burned-in subtitles with keyword highlight, animated big words, lower-third title, outro card, loudness-normalised voice, bed music, SFX |
| **Package** | HTML → PNG | covers in every platform's size, per-platform post copy with hashtag limits, a hand-off README |
| **Publish / Monitor** | design + stubs | see `docs/ARCHITECTURE.md` §6–7; adapters are the first community plug-in point |

Sample: `projects/2026-09-15-tangping/` — a 149 s talking-head recording became 4 videos, 10 covers and 12 posts.

## Quick start

```bash
brew install ffmpeg                     # macOS; Linux: apt install ffmpeg
npm install && scripts/make-sfx.sh      # Playwright (renders cards/covers offline) + CC0 placeholder sounds
python3 -m venv .venv && .venv/bin/pip install mlx-whisper   # Apple Silicon ASR
mkdir -p projects/2026-10-01-my-topic/source && cp ~/Movies/raw.mp4 projects/2026-10-01-my-topic/source/
cp projects/2026-09-15-tangping/{edit,copy}.json projects/2026-10-01-my-topic/   # then edit
python3 src/build.py projects/2026-10-01-my-topic
```

Write `script.md` (what you wrote), `voiceover.md` (what you actually said, incl. outro), then let the agent draft
`edit.json` (`.claude/skills/video-edit`) and `copy.json` (`video-package`). Everything the agent decides is a small JSON
you can read and change; everything fixed about *you* is in `config/profile.json`.

## Design principles

1. **Your style is config, not prompts.** Fonts, colours, cut rules, sound levels, outro — `config/profile.json`. Changed once, applied forever.
2. **Judgement is a JSON, not a video.** The agent writes `edit.json`; the pipeline renders it. You review 60 lines of text, not a timeline.
3. **Say *where* with words.** `"anchor": "温水煮青蛙"` — never seconds. Re-cut the video, anchors still hold.
4. **One cut, two languages.** Timing lives once in `work/plan.json`; zh/en differ only in text layers.
5. **Offline by default.** Rendering needs no network, no cloud editor, no upload. LLMs are used for *words*, never for *pixels* you can't check.
6. **Cheap tokens for bulk, expensive tokens for judgement, desktop agent for taste.** `config/llm.json` tiers.
7. **Source-available, personal use free, commercial licence for business.** See `LICENSE.md`.

## Docs
- `docs/ARCHITECTURE.md` — the seven stages, data model, agents/skills, security, token discipline
- `docs/PLAYBOOK.md` — how to actually work with it day to day; harness-agent vs graph-orchestration explained
- `docs/COMPETITIVE.md` — Buffer/Hootsuite/Metricool/新榜… what they do well, what we do differently
- `docs/ROADMAP.md` — looks & transitions, expression stickers, face-tracked crop, trend radar, sponsor inbox, analytics
- `CLAUDE.md` — the map an AI agent reads first

---

## 中文速览

**dot-dot-dot = 一条录像 + 一份文稿 → 全平台成片。** 自动去重录、按文稿上字幕（不是 ASR 错字）、大字弹出、贴片地图、片尾 logo、
横版 16:9 + 竖版 9:16、中文 + 英文、十个平台的封面尺寸和文案、发布队列、播放数据回流。个人风格写在 `config/profile.json`，
每条视频的判断写在 `projects/<slug>/edit.json`，位置一律用文稿里的原话做锚点，不用秒数。

- 一条命令：`python3 src/build.py projects/<日期-主题>`
- 样例：`projects/2026-09-15-tangping/`（《躺平》：149 秒素材 → 4 条成片 + 10 张封面 + 12 篇文案）
- 授权：个人免费（PolyForm Noncommercial），商用需付费授权，见 `LICENSE.md`
- 本地渲染、本地转写，录音不出电脑；LLM 只负责文字，贵模型做判断、便宜模型做翻译摘要，桌面端 agent 做品味
- 想改风格 → 改 `config/`；想改这条片 → 改 `edit.json`；想加平台 → 加一行 `config/platforms.json` + 一个适配器
