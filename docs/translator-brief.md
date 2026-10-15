# Translator brief - Dolucky no A.League Soccer (SNES, 1994)

You translate part of the Japanese text of "Dolucky no A.League Soccer" into English for a fan patch. It is a goofy
animal soccer game (cats, dogs, rabbits, bears and a team of mad-scientist moles) starring Dolucky, the cat mascot of
developer Zoom. The writing is jokey, self-aware 1994 game humour: keep every joke landing.
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.
Repo root: H:\translation\batch\projects\dolucky-no-a-league-soccer (run commands from there).

## Read first
1. `glossary.md` (short; binding names, rulings, style rules).
2. `build/terms_<batch>.txt` - glossary rows whose Japanese appears in your batch.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. ` / ` separates the screen lines of one string.
Rows are in display order: use neighbours for context.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Separate screen lines with `|` (no spaces needed
around it). Do not pad or centre: the merge centres lines itself. Plain ASCII only: straight quotes, `...`;
no tabs inside the English, no Japanese, no `[` + two hex digits + `]` (that is an escape in our encoder).
An empty Japanese line (blank row in the staff roll) gets an empty English line (`id<TAB>` with nothing after).

## Limits (hard; the check enforces them)
- Every screen line <= the `limit` in the row (characters, the font is fixed width 8 px).
- `story_pN`: one intro page = exactly 4 lines (`a|b|c|d`, blank lines allowed: `|Long ago...||`). 24 chars per
  line. You may move words between the 4 lines of a page freely, but each page keeps its own content.
- `quotes_*`: at most 2 lines of 28. `endmsg_00`: 24 per line, keep 3 text lines with a blank line between each
  (`a||b||c`), like the Japanese.
- `profiles_00`..`06` (name cards): at most 2 lines of 17. `profiles_07`..`20` (descriptions): at most 4 lines of 17.
- `credits_01.NNN`: one staff-roll line; 28 chars per line; you may use `|` to wrap one source line into two.
- If something cannot fit without losing meaning, keep the meaning, shorten wording, and report `LONG: id`.

## Staff roll (batch b1)
- Staff names: spell them exactly as the game's own English staff roll does (read the `jp` field of `credits_00`
  in `script/credits.json`: e.g. TAKAYUKI KAMIKURA, JUN-ICHI TAKEDA, SYUHEI IIDA). Given name first, UPPERCASE like
  that roll. Babies/other names not in it: Hepburn, uppercase.
- The kana line ドラッキーのAりーぐさっかー is the Japanese title: write `DOLUCKY NO A.LEAGUE SOCCER`.
- Job titles UPPERCASE as in the English roll (MAIN PROGRAMMER...). The jokey comment lines in mixed case.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Do not add facts. Adapt wordplay so
  the joke still lands (no translator notes in the text).
- Names and terms exactly as in the glossary. No abbreviations to fit (rephrase instead).
- Honorifics dropped (convey politeness/roughness through register). Given name first.
- Mixed case English. 「...」 -> "...". ・・・ -> "...". Use `!!` where the Japanese shouts.
- Voices: the cats are smug and lazy-cool ("Easy peasy"); the dogs earnest; the rabbits are rock-and-roll show-offs;
  the bears loud party guys ("Party time!"); the moles are sneering mad scientists. Staff-roll comments are dry
  in-jokes about the developers: keep them funny and a little deadpan.
- Kansai-dialect asides (e.g. そのまんまや ないけ) become a casual retort ("Well, duh. That's just what they did.").

## Consistency
Never edit `glossary.md` or any file other than your output. For a recurring name or term not in the glossary,
pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
