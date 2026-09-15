# dot-dot-dot — Design brief for a design AI

> 用法：把下面「PROMPT」整段复制给 Claude Design / Figma Make / Google Stitch / v0。
> 它描述的是我们已经在跑的产品（本地工作室 UI + 视频封面/卡片视觉系统），要求设计 AI 交付一套可落地的 UI/UX 与视觉规范。
> 品牌硬约束在 §2；页面清单在 §4；交付物在 §9。改动品牌规则请先改 `config/themes.json` / `config/profile.json`，再改这份简报。

---

## PROMPT

You are the lead product designer for **dot-dot-dot**, a local-first studio app for a single face-on-camera creator who publishes short talking-head videos in Chinese and English to ten platforms (小红书, 抖音, 快手, B站, YouTube, TikTok, Instagram, Facebook, LinkedIn, 公众号). The app is a window onto files: every screen reads and writes small JSON/Markdown files that an AI agent (Claude Code) also edits. The app must feel like a quiet editorial magazine studio, not a SaaS dashboard and not a video editor. Design the complete UI/UX and the on-video visual system described below. Be exhaustive: every screen, every state, every component, spacing, type, motion, copy. Where I give numbers, use them exactly; where I don't, decide and state the rule.

### 1. Who and why
- One user: an engineer-creator in New Zealand, Chinese first language, English fluent, records 2–3 minute talking-head videos on careers/business, wants a strong personal style he can defend and a workflow where he only writes, records, picks covers and approves.
- Second "user": an AI agent that edits the same files and runs the pipeline. Every screen must make agent-made changes visible (timestamps, diffs, "edited by agent 11:14") and let the human override in one click.
- Jobs to be done, in order of frequency: (1) review the auto-cut and tweak 2–3 overlays, (2) choose the cover frame/title/font/layout, (3) approve or schedule posts per platform, (4) read the speech-coach report, (5) glance at numbers, (6) change a global style rule once.

### 2. Brand — hard constraints
- **Never yellow/black. Never sticker/brutalist styling, no thick borders, no hard drop shadows, no emoji as UI.**
- Colour comes from a **theme** (one per video). Ship the UI on **Indigo Porcelain** and show that it survives the other eight:
  - Editorial: Ink Classic `paper #f3f0e8 ink #0a0a0b accent #111111`; **Indigo Porcelain** `paper #f2f4f5 paper-2 #e5ebef ink #0a1f3d muted #5f6d78 line rgba(10,31,61,.20) accent #315d93 accent-soft #d7e1ec`; Forest Ink `#f5f1e8 / #16251b / #2e6b4f`; Kraft Paper `#eedfc7 / #2a1e13 / #9b5a2e`; Dune `#f0e6d2 / #1f1a14 / #8f7650`; Midnight Ink (only dark) `paper #0e0d0c ink #ece2cf accent #d4a04a`.
  - Swiss: IKB Blue `paper #fafaf8 ink #0a0a0a accent #002FA7`; Lemon Green `accent #C5E803`; Safety Orange `accent #FF6B35`.
  - Tokens: `--paper --paper-2 --ink --muted --line --accent --accent-soft --accent-on`. Accent is used **once per view** (one link, one bar, one highlighted word). Everything else is paper/ink/muted/line.
- **Typography, editorial mode:** display = serif (`Noto Serif SC` for zh, `Playfair Display` for en) at **weight 400–500, tracking +0.03em**, never 700+ for large display ("the larger, the lighter"). Labels = `Inter` 500, uppercase, tracking +0.20em, 11–13 px. Body UI = system sans (PingFang SC / Inter) 14 px / 1.5. Swiss mode: `Inter` 300 for display, 600 for labels, no serif.
- Rules, not cards: separators are 1 px `--line` hairlines or grid gutters. Rounded radius 8–10 px max. No glassmorphism, no gradients in UI (gradients allowed only on the "photo" cover layout).
- Logo: three growing dots on a dotted arc, ink dots with the last dot in accent; wordmark ends with "…". Provide a 24 px app icon and a 16 px favicon derivation.

### 3. Global layout
- Desktop first (1440 × 900 baseline, works down to 1180; a read-only phone view at 390 px for queue/metrics/inbox only).
- Left rail 220 px in ink with paper text: logo, 5 items (Projects, Queue, Metrics, Inbox → Agent, Settings), footer line "human + agent share one file state", clock. Active item = accent text, no filled pill.
- Content area max 1500 px, 28 px padding, section titles 22 px serif 500, subsections 16 px.
- Top of every project view: slug + zh title in serif, then a **step bar** with 8 text buttons (1 transcribe · 2 plan · 2b translate · 3 cards · 4 assemble · 5 titles+covers · 6 speech · all) and a live job status line; a collapsible monospace log drawer (ink background, paper text, 12 px) opens under it while a step runs.
- Tabs under the step bar: 文稿 Script · 蓝图 Blueprint · 剪辑 Cut · 成片 Videos · 封面选型 Covers · 文案 Copy · 口播 Speech · 交接&发布 Handoff. Tabs are text with a 2 px accent underline on the active one.

### 4. Screens (design every one, all states: empty, loading, error, agent-edited, saved)
1. **Projects** — list of projects as rows (not cards): slug, title zh/en, a 7-dot progress strip (source, transcript, plan, cards, videos, covers, speech; done = accent-soft filled dot with ink ring, todo = line-only), counts (videos/covers/posts), last edited by (human/agent) + time, "Open". New project inline form: slug input with live validation `yyyy-mm-dd-topic`, hint where to drop the recording.
2. **Script** — two columns: `script.md` (what he wrote) and `voiceover.md` (what he said). Markdown editors with serif body, 16 px, 680 px measure. Below: a coverage badge (ASR↔script alignment %, red below 85 % with a one-line explanation "voiceover.md doesn't match the take").
3. **Blueprint** (the signature screen) — a node graph on a dark ink canvas with a 22 px dot grid. Seven vertical lanes with uppercase labels: Source · Cut · Layers & Sound · Assemble · Render · Package · Publish. Nodes 210 px wide, paper-2 on ink (or ink on paper — you decide, keep contrast ≥ 7:1), 1 px line border, 10 px radius, left 4 px colour key per node type (pop = accent, card = accent-soft, sfx = muted, music = paper-2, render = accent, publish = ink). Node shows title (13 px 600) and a one-line subtitle (12 px muted: anchor quote, duration, file). Input/output pins 10 px circles. Edges are 1.5 px accent bezier curves at 60 % opacity, drawn lane to lane; fan-in to a single Assemble hub, then fan-out to four Render nodes (16:9 zh, 16:9 en, 9:16 zh, 9:16 en), then Package, then ten Publish nodes. "+ add" nodes are dashed. Selected node = accent border + inspector panel docked at the bottom (not a modal): fields for anchor (script quote, with autocomplete from the script), text zh/en, hold seconds, style, sound (dropdown with inline audio preview), card template, JSON variables; a red "delete node" text button; "Save blueprint → edit.json", "Save & re-plan", "Save & rebuild". Show the unsaved state and a "saved 11:14:17" confirmation. Design drag-to-reorder within a lane and a future drag-to-connect affordance without implementing it.
4. **Cut** — left: `edit.json` code editor (monospace 12.5 px, paper-2 background) with validation. Right: a two-track timeline: track 1 source time (blue keep segments, muted-red cuts with tooltip reason), track 2 output time with markers (pop = accent dot, card = accent-soft dot, sfx = muted dot), a playhead; a video player below; a wrap of subtitle "chips" (clickable, strikethrough when skipped); a table of cuts with seconds and reasons.
5. **Videos** — four players in a 2×2 grid with filename, duration, size, "open folder".
6. **Covers** (second signature screen) — (a) contact sheet: 24 frames, 6 per row, timestamp badge bottom-left, selected frame gets an accent ring; (b) per language panel: frame seconds, kicker text, title HTML with a visual `<em>` toggle (click a word to make it the accent word), three title-option chips; (c) variants table: rows of font (dropdown showing the actual font sample and a "feel" label) × layout (editorial / swiss / photo / outline) × size × "pick" radio; "+ variant"; (d) rendered variants grid, click = pick; (e) **legibility strip**: every variant at 120 px wide on a grey band, with a caption "how it looks in a phone feed"; (f) link to hand 小红书 3:4 carousels to the external guizang skill. Make the pick action feel definitive (accent ring + "✓ used for youtube, bilibili…").
7. **Copy** — covers grid of ten platform sizes (labelled with platform and WxH), `copy.json` editor, per-platform post previews rendered as the platform would show them (title, first line, hashtags, truncated at the platform's limit with a counter).
8. **Speech** — coach notes (editable, serif) above an embedded report: sticky audio player, stats table, per-sentence table with play buttons (monospace pill), red rows = too fast, blue = too slow, strikethrough = cut retake; lists of breath points and mouth clicks with play buttons.
9. **Handoff & Publish** — table: platform, language, aspect, video, cover, copy file, schedule time, "add to queue". Explain in one sentence that publishing runs in the creator's own logged-in browser and stops before the final button unless confirmed.
10. **Queue** — table of posts: project, platform, language, time (editable), status pill (queued / prepared / confirmed / posted / needs human / failed — outline pills, accent only for "posted"), confirmed checkbox, post URL, screenshots link, error text. Global switch "auto-confirm" with a plain warning. Empty state explains how rows get here.
11. **Metrics** — per post: views/likes/comments/saves/shares at +1h/+24h/+7d/+30d as a small sparkline table; weekly digest text; "best hour" and "hook retention" tiles as text, not gauges. Empty state.
12. **Inbox → Agent** — a single textarea "tell the agent", optional project select, a list of requests with status open/done and the agent's one-line result. Copy: "写这里的每一条会进 ui/inbox.jsonl；在 Claude Code 里说「看任务箱」".
13. **Settings** — three JSON editors (profile / platforms / llm) plus a **theme picker**: nine swatches showing paper/ink/accent with the theme name and its intended use; switching previews the app chrome live.

### 5. On-video visual system (design as a separate "brand on video" page)
- 16:9 (1920×1080) and 9:16 (1080×1920) frames of a talking head; show every overlay in both aspects.
- Subtitles: sans 700, white with 4 px ink outline, one line ≤ 16 zh chars / ≤ 42 en chars, bottom margin 70 px (16:9) / 420 px (9:16); the keyword of the moment tinted with the theme's `videoHighlight` (Indigo: `#a9c7ea`).
- Keyword pops: display serif 400, paper colour with 3 px ink outline and a soft shadow, 140 px (16:9) / 120 px (9:16), −2° rotation, scale-in bounce 140 ms, sits right of the face (16:9) or top third (9:16). Corner counters ①②③ top-left.
- Lower third (first 3.2 s): title in serif on an ink box (paper text), subtitle sans white with thin outline; slides in from the left 320 ms.
- Picture-in-picture cards (map, quote, checklist): paper card, 1 px line, uppercase Inter label with one accent word, serif title 500, 46 % width right side (16:9) / 62 % width top (9:16), 250 ms alpha fade, must never cover the face.
- Outro (4 s): paper background, logo in a paper-2 circle, 1 px rule, serif headline with one italic accent word, uppercase CTA in muted, handle in accent.
- Covers: four layouts — **editorial** (paper panel left 50 %, kicker with 56 px rule, serif title, italic accent word; photo on the right, face centred in the photo half), **swiss** (ink panel, Inter 300 title, accent bar), **photo** (full bleed, ink gradient from the text side, paper serif), **outline** (YouTube classic white text with ink stroke). Portrait variants stack the panel on top at 36 % height. Deliver all ten platform sizes for one video.

### 6. Interaction and motion
- No spinners: progress is text ("assemble · 9x16 zh · 42 s") and a 1 px accent progress hairline under the step bar.
- Motion budget: 120–320 ms ease-out, only for panel dock, node select, tab underline, cover pick ring. Nothing bounces in the UI (bounce is reserved for on-video pops).
- Keyboard: `⌘S` saves the current file, `J/K` moves between nodes, `Space` toggles the player, `1–8` switches tabs.
- Agent presence: a thin line under any field the agent changed since you last looked, with "agent · 11:14 · reason". Accepting = doing nothing; overriding = editing.
- Destructive actions (delete node, remove queue row, clear done) are text buttons in a muted red `#b3402f`, never filled, with undo toast for 6 s.

### 7. Content and tone
- Bilingual UI labels: Chinese first, English second in muted, e.g. "封面选型 Covers". Numbers and file names never translated.
- Microcopy is plain and short; explain *why* in one clause ("字幕以 voiceover.md 为准，不是 ASR"). No exclamation marks, no emoji.

### 8. Accessibility and states
- Contrast ≥ 4.5:1 for all text on paper; ≥ 7:1 on the blueprint canvas. Focus rings 2 px accent. All tables sortable, all images with alt text (cover: title + platform).
- Every screen: empty (first-run guidance in one paragraph), loading (text), error (what failed + the file to fix), read-only (when the agent holds a job on it).

### 9. Deliverables
1. Figma file with pages: Foundations (tokens for all nine themes, type scale, spacing 4/8/12/16/24/32/48, iconography — thin 1.5 px line icons only), Components (rail, step bar, tabs, node, edge, inspector, timeline, chips, tables, pills, editors, contact sheet, variant row, legibility strip, toast), Screens (all 13 at 1440 wide, Indigo Porcelain), Theme proof (Blueprint + Covers screens re-skinned in Ink Classic, Midnight Ink, IKB Blue), Brand-on-video (16:9 and 9:16 boards with every overlay), Covers (10 platform sizes × 4 layouts), Mobile (queue, metrics, inbox at 390).
2. A one-page written rationale: how the editorial rules translate to a working tool, and three things you refused to add and why.
3. CSS custom properties for the tokens and a type scale table, ready to paste into `templates/cards/_base.css` and `src/ui/index.html`.

Do not invent features beyond this brief. If a screen needs a control I did not list, add it and mark it "proposed".

---

## 中文速览
这份简报交给设计 AI 后，它应当交付：13 个界面（Indigo Porcelain 主题）+ 3 个主题换肤证明 + 视频内视觉系统（字幕、大字、下三分之一、贴片、片尾）+ 10 个平台 × 4 种版式的封面 + 组件库与 token。硬约束：绝不黄黑、绝不贴纸风；一套主题一个强调色、每屏只用一次；编辑风排版「越大越轻」；界面无状态，人和 agent 共用文件。
