# Contributing

The project lives or dies by three plug-in points. Pick one:

| Plug-in | Where | What a PR looks like |
|---|---|---|
| **Platform adapter** | `src/publish/adapters/<platform>.py` + a row in `config/platforms.json` | the upload/schedule clicks for one platform's web studio, with a recorded Playwright trace and `verified: <date>` |
| **Card / cover template** | `templates/cards/*.html`, `templates/covers/*.html` | one HTML file, `{{vars}}` documented at the top, a PNG preview in the PR |
| **Asset pack** | `assets/manifest.json` entries | URL + licence + attribution for every file; CC0 / CC-BY / paid-with-proof only |

Rules
- English in code, comments, commits, docs. README gets a 中文速览 section at the end.
- Never commit media from `projects/*/source` or `output`.
- A change to the pipeline updates `CLAUDE.md` in the same commit.
- By contributing you agree your contribution may be distributed under LICENSE.md and COMMERCIAL-LICENSE.md.

Community: GitHub Discussions for ideas, Issues for bugs, `#showcase` for videos made with the tool.
