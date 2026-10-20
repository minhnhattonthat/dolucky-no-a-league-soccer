# Dolucky no A.League Soccer English translation

Unofficial English fan translation of **Dolucky no A.League Soccer** (Super Famicom, Imagineer / Zoom, 1994): the
source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What's translated

The attract-mode intro story, team and character profile cards, ending quotes and message, the Japanese staff roll
with its jokes, player names on the match HUD, the hidden Bonus Mode and Debug Mode menus, and the Japanese title
subtitle. Menus, HUD and team names were already English in the original. Lowercase letters were added to the font.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `build.py`, `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |

## Build your own patched ROM

Needs Python 3.12+ (pytest for the checks), the
[translate-retro-game](https://github.com/minhnhattonthat/translate-retro-game) skill (set `SKILL` to the directory
holding its SKILL.md) and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/dolucky-no-a-league-soccer
cd dolucky-no-a-league-soccer
# copy your dump to: rom/Dolucky no A.League Soccer (Japan).sfc
#   (1572864 bytes, headerless, SHA-1 e5548e359558ff6c044fd7f4f52c85434ae45c21; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/dolucky_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Imagineer's and is included only so
the translation can be checked against it. Dolucky no A.League Soccer is (c) Imagineer; this project is not affiliated
with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
