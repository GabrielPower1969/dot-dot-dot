---
name: trend-radar
description: Nightly scan of trending topics (RSS, platform trending pages, 3–5 peer accounts) filtered by the creator's industries, producing ideas/<date>.md with three hooks per topic and a why-now line. Cheap LLM tier. Use when the user asks 热点/选题/what should I record.
---
Sources in `config/trends.json` (planned): RSS list, platform trending URLs, peer handles. Output ≤ 10 topics, each: title, why-now (with source URL), 3 hooks (zh), 1 hook (en), fit score 1–5 against `config/profile.json.creator.industries`. Never fabricate a source; mark unverified claims [C].
