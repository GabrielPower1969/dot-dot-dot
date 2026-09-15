# assets

| Folder | What | Licence rule |
|---|---|---|
| `fonts/` | Arimo, Noto Sans SC | OFL 1.1, bundled |
| `brand/` | logo.png (outro/watermark), wordmark.svg | yours |
| `sfx/` | pop, ding, whoosh, bleep, thud — **synthesised placeholders (CC0)**; replace with real recordings via manifest | every file needs a manifest row |
| `music/` | `placeholder-lofi-pad.wav` (synthesised) — replace with licensed beds by mood | manifest row with licence + attribution |
| `broll/` | clips/stills referenced by `edit.json.inserts[card=broll]` | manifest row; AI-generated stills must be labelled |

`manifest.json` rows: `{ "file", "source_url", "licence", "attribution", "mood|use", "added" }`. `scripts/fetch-assets.sh` (planned) downloads by manifest.
Good sources: freesound.org (filter CC0), pixabay.com/sound-effects (Pixabay licence), mixkit.co (Mixkit licence), YouTube Audio Library (attribution rules per track), Kevin MacLeod / incompetech (CC-BY 4.0). Paid: Epidemic Sound, Artlist — keep the invoice in `assets/licences/`.
