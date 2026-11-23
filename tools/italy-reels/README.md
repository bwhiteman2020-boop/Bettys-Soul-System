# Italy reels (Dolce Vista) — Vinny tooling

Scripts that built the 10 Italy reels on the Dolce Vista canvas
(https://claude.ai/artifact/Y3ZvYe5dvpeujvVf6hRNZ2, artboard "Italy reels · 10 videos").

- `compose.py` — writes 3 original, royalty-free instrumentals (dolce, memoria, passeggiata) with numpy: `python3 compose.py music`
- `jobs.py` — the 10 reel plans (segments, hooks, cards, end-card quotes, sound mode). Run it to write `jobs.json`.
- `build.py` — renders each job to 1080x1920/30 fps: Dolce Vista grades (Travertino, Canale, Memoria), Cormorant Garamond hooks centered mid-frame, Twilight message cards, cream arch end card, music or natural sound. `python3 build.py [job ids]`

Expected working-folder layout (next to the scripts):
- `src/` — `rome.mov`, `venice.mov`, photos `1.jpg`–`5.jpg`
- `masters/` — `<clip>_rt.mp4` (1080x1920, 30 fps) and `<clip>_slow3.mp4` (3x slow motion via ffmpeg minterpolate)
- `fonts/` — `CormorantGaramond[wght].ttf`, `CormorantGaramond-Italic[wght].ttf`, `Jost[wght].ttf` (Google Fonts, OFL)
- `music/` — output of `compose.py`

Needs Python 3 with numpy and Pillow, and FFmpeg. Keep footage and renders out of the vault.
