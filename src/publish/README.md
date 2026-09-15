# publish — queue + browser adapters (design; adapters are stubs)

`queue.json` rows: `{ "slug", "platform", "lang", "at": "2026-09-17T19:00+12:00", "status": "queued|prepared|confirmed|posted|failed", "url": null }`
`python3 src/publish/queue.py run` (cron/launchd every 15 min): for rows due and `confirmed`, call the adapter's `submit`; otherwise `prepare` and leave a screenshot in `publish/screens/`.
Adapters implement `prepare(row) -> png`, `submit(row) -> url`, `verify(url) -> bool` on a Playwright *persistent* context at `~/.dotdotdot/browser/<platform>`. See `adapters/base.py`.
