---
name: video-package
description: Write projects/<slug>/copy.json (per-platform titles, hook, body, CTA, hashtags, cover title, cover frame time, publish order) from edit.json + script, respecting config/platforms.json limits, then run step 5 and review the covers. Use after a video is edited or when the user asks for 文案/封面/标题.
---
# video-package
1. Cover frame: sample 12 frames from `work/intermediate/cut.16x9.mov`, pick mouth-closed + eye contact (smile if the topic allows). Set `cover_time_s`.
2. Cover title ≤ 12 zh chars / ≤ 6 en words, the *claim*, with one `<em>` word. Kicker = the situation ("找工作前先想清楚").
3. Titles per platform: 小红书 ≤ 20 chars, emoji-free, curiosity gap; 抖音 first 10 chars carry the hook; B站 adds 【tag】; YouTube ≤ 60 chars, no clickbait words that trigger review; LinkedIn has no title — body is the post.
4. Hashtags within `tags_max`; zh and en sets differ; 3 broad + 3 niche + 1 location.
5. Body: hook (one line) → 3 bullets → CTA question. LinkedIn body is a rewrite in first person, English, no emoji.
6. `publish_order` and `schedule`: 小红书 and 抖音 first (evening NZ = afternoon CN), YouTube/LinkedIn next morning NZ.
7. `node src/steps/5-package.js projects/<slug>`; open two covers (16:9, 9:16) and fix overflow before handing off.
