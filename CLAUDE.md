# Dolucky no A.League Soccer (SNES) English translation

Skill: translate-retro-game (H:\translation\batch\.claude\skills\translate-retro-game\SKILL.md). Read it before ROM, text or QA work. Batch brief: H:\translation\batch\projects\BATCH_BRIEF.md.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/dolucky_en.sfc (`--mode identity|marker`, `--qa ID=text`)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this)
- Extract:  `python -X utf8 tools/extract.py` (never clobbers `en`; `--force` re-reads jp and keeps en/status/notes)
- Smoke:    `python -X utf8 H:\translation\batch\.claude\skills\translate-retro-game\scripts\emu.py build/dolucky_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py SCENE [--rom build/dolucky_en.sfc]` (scene list in tools/debug/scenes.py; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (gate + BPS + verify; never publish)

## Paths
- Original ROM: `rom/Dolucky no A.League Soccer (Japan).sfc` (gitignored; CRC32 0BC19D72, SHA-1 e5548e359558ff6c044fd7f4f52c85434ae45c21).
- Emulator: `tools/mesen/` MesenCE 2.2.1 (github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored).
- Text: `script/<group>.json` (jp/en per string, `\n` = code 01). Groups and refs: `tools/textdefs.py`. Tables: `tbl/`.
- RE notes: `docs/re/text.md` (encoding, printer task, text groups, secrets), `docs/re/graphics.md` (graphics text).
- Glossary + rulings: `glossary.md`.

## Rulings (pre-approved, BATCH_BRIEF)
- Edit source only with the file-edit tool. Full names, no abbreviations (engine work first). Honorifics dropped;
  given name first. Romanization: official English (team names are already English in the game's own graphics), else Hepburn.
- Credits translated. Graphics text (title subtitle) in scope. Never push/publish; release = local zip.

## Status
- Done: Step 0, phase 1 recon (text found, encoding, refs), phase 3 identity, phase 4 extract. Next: debug tool (phase 2), font lowercase + marker build (phase 5). Open bugs: none.
