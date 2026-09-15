---
name: sponsor-inbox
description: Triage sponsorship / 商单 emails from the Gmail label "sponsor" into deals/<brand>.md (brand, ask, budget, deadline, fit, red flags) and draft a reply using the rate card in config/ratecard.json — drafts only, never send. Use when the user asks about 广告/商单/sponsor emails.
---
Read only; write `deals/<brand>.md` and a Gmail *draft*. Fit check against `profile.rules` and the brand-safety list. Flag: crypto/gambling/MLM, exclusivity > 30 days, usage rights beyond 12 months, payment > 30 days. Quote the rate card; never invent a price.
