# Ingest Log

Append-only. One entry per ingest, query, or lint pass.

Format:
- [INGEST] YYYY-MM-DD — source title — pages touched
- [QUERY] YYYY-MM-DD — question — answer saved to
- [LINT] YYYY-MM-DD — issues found/fixed

---

- [INGEST] 2026-08-27 — `betty-whiteman-profile` skill (SKILL.md + references/full-profile.md) — pages touched: wiki/founder-profile.md
- [INGEST] 2026-08-27 — `pattern-and-power-starter-kit` skill (SKILL.md + 5 references/*.md) — pages touched: wiki/power-and-pattern-coaching/01-identity-and-positioning.md, 02-brand-voice.md, 03-ideal-client.md, 04-programs-and-offers.md, 05-market-and-competitors.md, company-details.md
- [INGEST] 2026-08-27 — `power-and-pattern-ai-profile` skill (SKILL.md) — pages touched: wiki/power-and-pattern-ai/01-identity-and-positioning.md, 02-brand-voice.md, 03-ideal-client.md, 04-programs-and-offers.md, company-details.md, wiki/design-systems/power-and-pattern-ai-brand-colors.md
- [INGEST] 2026-08-27 — combined founder + both-brand ingest — new pages created: wiki/glossary.md, wiki/dreams.md, wiki/best-content.md (starter), index.md, CLAUDE.md, sources/README.md
