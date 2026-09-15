# Roadmap

Ordered by what unblocks the next video, not by how impressive it is.

## v0.2 — the details Gabriel cares about
- [ ] **Real sound library**: `assets/manifest.json` with CC0/CC-BY footsteps, whooshes, risers, record scratch, bleep, comedic boing, 3–4 bed tracks by mood (calm / tense / playful); `scripts/fetch-assets.sh` downloads by manifest and writes attribution into `output/README.md`.
- [ ] **Scene music**: `edit.json.music[{anchor_from, anchor_to, mood}]` swaps the bed with ducking (`sidechaincompress`).
- [ ] **Looks per scene**: `edit.json.looks[{anchor, look}]` → `memory` (warm + vignette + 12 fps stutter), `news` (cool, sharp), `dream` (bloom). Transitions between scenes only: whip-pan `xfade`, 8-frame dip-to-brand-yellow; none inside talking head.
- [ ] **Expression stickers**: pack of 12 PNG/APNG (blush, big eyes, shock, sweat drop, question marks, 💡) anchored to the face box; `edit.json.stickers[{anchor, sticker}]`.
- [ ] **Face-tracked 9:16 reframe** (step 1b, mediapipe): smooth crop path instead of fixed centre; keeps PiP clear of the head automatically.
- [ ] **Speech coach v2**: breath-point and lip-smack detection with audio cleanup (`afftdn`, de-click), per-sentence pace targets.
- [ ] **Logo animation**: 3 s outro with the dots connecting (SVG SMIL → PNG sequence), fixed bottom-right watermark.

## v0.3 — distribution
- [ ] Adapters: 小红书, 抖音, B站, YouTube, TikTok, Instagram/Facebook (Meta Business Suite), LinkedIn, 快手 — confirm-first, persistent browser profiles, receipts.
- [ ] `queue.py` + launchd job; `publish/queue.json` editable by hand.
- [ ] Auto-clips: 1–3 vertical 45 s cuts from `edit.json.clips[]` anchors.

## v0.4 — numbers and money
- [ ] Monitor pull (+1 h / +24 h / +7 d / +30 d), `metrics/*.jsonl`, static HTML dashboard.
- [ ] Weekly digest (cheap tier): retention on hook, best hour, comments to answer.
- [ ] Sponsor inbox: Gmail label → `deals/<brand>.md` with rate card, draft reply, never auto-send.
- [ ] Ad/brand-safety checklist per platform before publish.

## v0.5 — trend radar
- [ ] RSS + platform trending pages + 3–5 peer accounts → `ideas/<date>.md` with three hooks each, tagged by industry.

## Later
- n8n bridge (shell nodes calling the steps) for non-engineer collaborators; community adapter registry; AI-generated
  scene stills (labelled) for B-roll; Windows/Linux ASR path (faster-whisper).
