# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `tools/font.py` (`LOWER`) | drawn for this project (1-px skeletons, outline generated like the game's uppercase) | MIT, same as repo | yes | lowercase a-z in the 8x16 text font (codes 43-5C) | - |
| `tools/title_gfx.py` | drawn for this project (small outlined pixel font) | MIT, same as repo | yes | English title subtitle sprites | - |
