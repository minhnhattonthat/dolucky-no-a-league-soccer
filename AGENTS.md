# Dolucky no A.League Soccer (SNES) English translation

Skill: translate-retro-game (Claude Code: plugin `translate-retro-game@retro-translation`; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md). Read it before ROM, text or QA work. Tools take the skill's `scripts/` from `$SKILL`, else the newest installed plugin copy (`tools/textio.py`).

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/dolucky_en.sfc (checks the dump against `rom.sha1` first; `--mode identity|marker`, `--qa ID=text`)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this; tests skip without the ROM)
- Extract:  `python -X utf8 tools/extract.py` (never clobbers `en`; `--force` re-reads jp and keeps en/status/notes)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/dolucky_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py SCENE [--rom build/dolucky_en.sfc]` (scene list in tools/debug/scenes.py; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (gate + BPS + verify -> release/dolucky-no-a-league-soccer_en.zip with `docs/release-readme.txt`; never publish without the user)

## Paths
- Original ROM: `rom/Dolucky no A.League Soccer (Japan).sfc` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`; CRC32 0BC19D72). Emulator: `tools/mesen/` MesenCE 2.2.1 (github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored).
- Text: `script/<group>.json` (jp/en per string, `\n` = code 01). Groups and refs: `tools/textdefs.py`. Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Translation workflow: `tools/batches.py split|check|merge` (work/tl/), brief `docs/translator-brief.md`.
- Gotchas: only the ASCII the font has (glossary.md); no `[XX]` in text (hex escape). The patch expands the ROM to 2 MB (`ROM_SIZE`); start QA from a cold boot, not a Japanese-ROM savestate.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
