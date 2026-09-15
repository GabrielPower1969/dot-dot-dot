# materials/ — drop zone (you find it, the agent places it)

Put anything you want in the cut here: B-roll clips, screenshots, memes, music, SFX, stickers, reference images.
Optional `materials.json` next to them tells the agent *where* and *how*; without it the agent proposes placements in edit.json for you to approve.

```json
[
  { "file": "hormuz-news.mp4", "anchor": "伊朗扼守霍尔木兹海峡", "as": "cutaway", "hold_s": 4, "note": "keep my voice, mute clip" },
  { "file": "frog.png",        "anchor": "温水煮青蛙",           "as": "pip",     "hold_s": 2.5 },
  { "file": "bgm-calm.mp3",    "as": "bgm", "from_anchor": "真正能让人躺平", "to_anchor": "你学会了吗", "db": -28, "licence": "Epidemic invoice #1234" },
  { "file": "record-scratch.wav", "anchor": "这叫温水煮青蛙", "as": "sfx" }
]
```
`as`: cutaway (full-frame, voice continues) · pip (card-sized overlay) · bgm (scene music with ducking) · sfx · sticker (face-anchored, v0.2).
Every audio file needs a `licence` line or the build warns. Nothing in this folder is committed to git.
