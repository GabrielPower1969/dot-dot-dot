# Thumbnail rules — sources and evidence level

**A · read 2026-09-16** — sergebulaev/youtube-skills `references/thumbnail-principles.md` (MIT, © 2026 Sergey Bulaev). Distilled, not copied:
one focal point · a legible genuine emotion · high contrast/separation · ≤ 3–4 words that don't repeat the title · must read at 120 px on a phone ·
rule of thirds, face off-centre, text opposite · gaze direction pulls the eye · red/yellow/cyan contrast · always 2–3 concepts varying one element.

**B · read 2026-09-16, no licence stated (cited, not copied)** — pottertech/claude-skills `youtube/thumbnail-design`: 3–5 words max, heavy sans, no thin/script;
text in upper area (bottom 25 % gets the duration badge); face close-up 40–60 % of frame, eye contact; ≤ 3 visual elements; 168×94 px legibility check.

**Tools evaluated (2026-09-16)**
| Skill | Verdict |
|---|---|
| op7418/guizang-social-card-skill (7k★, HTML→PNG via Playwright, offline, AGPL-3.0) | **Use** for 小红书 3:4 carousels and 公众号 21:9+1:1 pairs. Installed at `~/.claude/skills/`. Themes are locked (no custom hex) — that is a feature. |
| Vivixiao980/xhs-cover-skill (MIT, 18 styles) | Not used: generates covers with an image model (GPT Image / Gemini) — alters the creator's photo, needs an API, not reproducible. Style list is a good mood board. |
| aabrole/claude-video-thumbnail-skill | Not used: Gemini image generation; long-form vs short-form routing idea adopted in this skill. |
| sliday/google-fonts-skill (MIT, MCP) | Not used: Latin only; our `fonts.json` carries the CJK set. |
| bergside/awesome-design-skills | 67 UI design-system skills; none about covers/typography. |

**Fonts** — all OFL-1.1: Noto Sans/Serif SC, Smiley Sans (得意黑), ZCOOL KuaiLe, ZCOOL QingKe HuangYou, Ma Shan Zheng, Zhi Mang Xing, Long Cang, Anton, Bebas Neue, Archivo Black, Oswald, Arimo. `scripts/fetch-fonts.sh` downloads them; `assets/fonts/fonts.json` is the only place a font may be referenced from.
