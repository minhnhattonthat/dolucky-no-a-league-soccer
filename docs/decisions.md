# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-15 | Honorifics and name order | keep (-san), drop; JP or Western order | Dropped, conveyed through register; given name first. Pre-approved in the batch brief. |
| D2 | 2026-10-15 | Romanization source for names | official art, earlier patch, Hepburn | The game's own English graphics (team names, English staff roll) first, else Hepburn. |
| D3 | 2026-10-15 | Credits | stay Japanese, translate | Translated, jokes kept; staff names as in the game's English roll. |
| D4 | 2026-10-15 | Abbreviations | engine work first (default), abbreviate | None: lowercase font, widened boxes, 2 MB expansion instead. |
| D5 | 2026-10-15 | Graphics text left in Japanese | none (default), list | None: the title subtitle is redrawn (LZ codec, tools/title_gfx.py). |
| D6 | 2026-10-15 | Specs and plans | need approval, pre-approved | Pre-approved (batch brief): work through the phases, report at the end. |
| D7 | 2026-10-15 | Release | publish, local only | Local zip only (release/, gitignored); never push or publish without the user. Replaced by D8. |
| D8 | 2026-10-20 | Publish v1.0 | publish, keep local | User: "publish it to github with the v1.0 release". Public repo minhnhattonthat/dolucky-no-a-league-soccer, release v1.0 (.bps + zip). |
