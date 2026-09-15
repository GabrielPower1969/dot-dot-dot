---
name: cover-design
description: Design the cover/thumbnail set for a talking-head video — the creator picks the frame, title, font and style; the skill produces 3–4 variants per platform size, a 120 px legibility strip, and routes 小红书 carousels / 公众号 covers to the guizang-social-card-skill. Use whenever the user mentions 封面/缩略图/thumbnail/cover/标题字体/海报 for a video.
---
# cover-design

The cover is the creator's decision. This skill *prepares choices and enforces rules*; it never picks the final frame alone.

## Inputs
`projects/<slug>/copy.json` (`<lang>.cover` block), `work/intermediate/cut.16x9.mov`, `assets/fonts/fonts.json`, `config/platforms.json`, `references/thumbnail-rules.md`.

## Workflow
1. **Contact sheet** — in the studio UI (封面 tab) or `GET /api/frames?slug=<slug>&n=24`: 24 frames evenly spaced. Ask the user to pick 1–2; prefer eyes open, mouth closed or mid-smile, gaze at lens, head off-centre. Never pick for them; you may mark 3 candidates.
2. **Title** — 3 options per language, each ≤ 4 zh "beats" (≈ 8–12 chars) / ≤ 4 en words, **not** the video title verbatim, one `<em>` word (the one the eye must catch). Put them in `copy.<lang>.cover.title_options`; the user chooses `title_html`.
3. **Font + style** — offer 2 fonts from `fonts.json` that match the *emotion* (权威→noto-black/anton · 搞笑→kuaile · 走心→mashanzheng · 冲击→longcang/bebas · 年轻→smiley) and 2 styles (`outline` YouTube classic, `block` bars, `yellow`, `clean`, `red`). Record as `copy.<lang>.cover.variants: [{font, style}]` (3–4 entries).
4. **Render** — `node src/steps/5-package.js projects/<slug>` writes `output/covers/<platform>.<lang>.<WxH>.v<N>.png` per variant plus `output/covers/legibility-<lang>.png` (every variant shrunk to 120 px wide, side by side).
5. **Legibility test** — look at the strip. A variant fails if the `<em>` word or the face is not readable at 120 px. Say which fail and why; the user picks the winner → set `copy.<lang>.cover.pick: N`; re-run package to name the winner without suffix.
6. **小红书 / 公众号** — for a 3:4 carousel or a 21:9 + 1:1 WeChat pair, invoke `guizang-social-card-skill` with the chosen frame as the user image and the chosen title; save outputs under `output/xiaohongshu/cards/`. (That skill is AGPL-3.0 and lives in `~/.claude/skills/`; it is a tool we call, not code we ship.)

## Rules (see references/thumbnail-rules.md for sources)
- One focal point; face fills 40–60 % of a 16:9 frame, off-centre, text on the other side.
- ≤ 4 words / ≤ 12 zh chars; heavy weight; stroke or shadow; one contrasting word.
- Keep the bottom-right 25 % of 16:9 clear (duration badge); keep the bottom 20 % and right 12 % of 9:16 clear (platform UI).
- Genuine expression matching the content; no stock smile on a warning video.
- Always ship 3 variants that differ in **one** element (font / style / frame) so the numbers teach something.

Never: AI-alter the creator's face, download stock faces, use a font not in `fonts.json` (licence tracked), change `templates/covers/cover.html` for one video.
