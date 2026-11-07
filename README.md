# Hidden Mechanics

Animated YouTube Shorts explaining how everyday things actually work, made end to end by Claude.

Channel: https://www.youtube.com/@Hidden.Mechanics.Channel

- `pipeline/PIPELINE.md` — the daily runbook (topic → fact-checked script → voice → animation → render → upload)
- `pipeline/hm/` — the engine (`python3 -m hm.studio voice|stills|video EP_DIR`)
- `pipeline/episodes/` — one folder per episode (script, scenes, metadata)
- `pipeline/episodes.json` — log of every episode
- `videos/` — finished shorts (the upload page pulls them from here)
- `branding/` — logo, banner, watermark
