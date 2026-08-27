# Sources

Raw, immutable clips. Drop things here. Never edit files once saved.

## How to add a source

**Option 1 — URL in chat:** Paste a link and say "ingest this." Claude fetches it, extracts what matters, updates the wiki, and saves the raw content here automatically.

**Option 2 — Save a file here manually:** Use a browser extension (MarkDownload, Obsidian Web Clipper, etc.) to save a page as markdown. Drop it in this folder with the naming format: `YYYY-MM-DD-short-title.md`. Then say "ingest [filename]" and Claude does the rest.

## What happens on ingest

Claude reads the source, updates the relevant wiki pages (tagging which brand — Power & Pattern™ coaching or Power and Pattern AI — where the content is brand-specific), updates `index.md` if needed, and appends to `log.md`. The raw file stays here untouched as the source of truth.

## First Ingest (2026-08-27)

The initial wiki content in `wiki/founder-profile.md`, `wiki/power-and-pattern-coaching/`, `wiki/power-and-pattern-ai/`, and `wiki/design-systems/power-and-pattern-ai-brand-colors.md` was ingested directly from four existing Claude skills already loaded in this account, not from a pasted URL or file:

- `betty-whiteman-profile` (SKILL.md + `references/full-profile.md`)
- `pattern-and-power-starter-kit` (SKILL.md + all 5 `references/*.md`)
- `power-and-pattern-ai-profile` (SKILL.md)

No raw clip is saved here for that ingest since the sources were skill files, not web content — the skills themselves remain the source of truth for that first pass. See `log.md`.
