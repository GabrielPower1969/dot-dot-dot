# monitor — numbers back from the platforms (design; stubs)

`pull.py <slug>`: for each posted row in `publish/queue.json`, scrape the creator dashboard (browser) or API (YouTube Data API v3, LinkedIn, Meta Graph) at +1 h/+24 h/+7 d/+30 d, append `{t, platform, views, likes, comments, saves, shares, avg_watch_s}` to `metrics/<slug>.jsonl`.
`digest.py --week`: cheap-tier summary → `metrics/digest-<date>.md`; `dashboard.py` → `metrics/index.html` (static, no server).
`trends.py`: trend radar sources (RSS, trending pages, peers) → `ideas/<date>.md`.
