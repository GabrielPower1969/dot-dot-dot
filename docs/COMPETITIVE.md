# Competitive notes — publishing, monitoring, dashboards

Evidence level per the audit rules: everything below is **[D · my working knowledge, verified 2026-09-16 = not yet]**.
Before quoting any of it externally, open each product's pricing/feature page and mark the row `verified`.

| Product | Publishing | Monitoring / analytics | Dashboard | Video editing | zh platforms | Price model |
|---|---|---|---|---|---|---|
| Buffer | schedule to IG/FB/LinkedIn/X/TikTok/YouTube/Pinterest via APIs | basic per-post stats | web, clean, per-channel | none | none | free tier + per-channel |
| Hootsuite | same set + approval workflows | strong listening, team reports | dense, enterprise | none | none | expensive, team-oriented |
| Later / Planoly | IG-first visual planner, link-in-bio | IG analytics, best time | grid preview | none | none | per-social-set |
| Metricool | multi-platform + competitor tracking | strong, exportable | good, affordable | none | none | freemium |
| Publer / SocialPilot | bulk CSV scheduling, AI captions | medium | ok | none | none | cheap per-account |
| OpusClip / Descript / CapCut | — | — | — | auto-clips, captions, templates | CapCut yes | subscription |
| 新榜 / 蝉妈妈 / 灰豚 | — | deep 抖音/小红书/B站 data, trending, competitors | web | none | native | expensive, agency-oriented |
| 壹伴 / 微小宝 / 蚁小二 | multi-account 公众号/抖音/小红书 posting | basic | web | none | native | cheap-ish |

What they do well that we should copy
- **Best-time-to-post from your own history** (Metricool, Later) → stage 8 digest, once we have 20 posts.
- **Approval step with screenshot** (Hootsuite) → our confirm-first adapters already do this.
- **Competitor tracking** (Metricool, 新榜) → trend radar should pull 3–5 peer accounts, cheap tier summarises.
- **Auto-clips from long video** (OpusClip) → planned: `edit.json.clips[]` cuts a 30–60 s vertical from anchors.

Where none of them fit a bilingual solo creator (our gap)
- Nobody spans **抖音/小红书/B站 + YouTube/TikTok/LinkedIn** in one queue; Western tools can't post to Chinese
  platforms (no APIs), Chinese tools don't touch the Western ones. Browser-driven adapters do both.
- Nobody starts from the **recording**. They start from a finished MP4; we own the cut, the style and the copy, so
  the covers, titles and hashtags are *derived from the same edit.json*, never re-typed.
- Nobody stores your **taste as config** you can diff. Their "brand kits" are fonts and colours; ours includes cut
  rules, sound levels, and written rules the agent obeys.
- All are SaaS with your media on their servers. We render and transcribe locally.

What we should *not* build: team inboxes, client approval portals, social listening at scale. That is Hootsuite's
business and needs a team to run.
