---
name: video-publish
description: Publish a packaged project to platforms through the user's logged-in browser (Chrome MCP or Playwright persistent profile), one platform at a time, filling video/cover/title/copy/hashtags/schedule and STOPPING before the final submit until the user confirms. Use when the user says 发布/发/publish/schedule.
---
# video-publish
Read `projects/<slug>/output/README.md` (the hand-off table). For each platform in `publish_order`:
1. Open the creator studio URL from `config/platforms.json.publish`. If not logged in, stop and ask the user to log in (never type credentials).
2. Upload the video file for that platform's aspect, set the cover PNG, paste title/body/hashtags from the post .md, set schedule time.
3. Screenshot the filled form, show it, ask "post / schedule <platform>?" — proceed only on an explicit yes for *this* platform.
4. After submit, capture the post URL into `publish/receipts.jsonl` `{slug, platform, lang, url, at}`.
5. Cookie/consent banners: decline non-essential. Never accept new terms on the user's behalf.
Platform notes live in `src/publish/adapters/<platform>.md` — update them when a page changes (date it).
