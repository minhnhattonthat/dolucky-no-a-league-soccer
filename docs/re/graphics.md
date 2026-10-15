# Graphics text survey (phase 1/8)

Toured with the debug warps (title, attract story/profiles/PK demo, mode select, VS/tour select, match HUD, stats,
continue, all endings, credits, true-ending stage). Everything tile-drawn is already English except:

| screen | element | source | status |
|---|---|---|---|
| title | subtitle ドラッキーのAりーぐさっかー | OBJ sprites 18-25 (8 x 16x16, 4bpp, pal 2), LZ block file 6CE1C (VRAM $6000) | English "DOLUCKY'S A-LEAGUE SOCCER" (tools/title_gfx.py), recompressed in place |

LZ codec: tools/lz.py (decompressor at $80:F28D; format in its docstring). Decompression log: tools/lua/lzlog.lua.
Not reached with the debug tool: the plain OPTION screen (attempt in warp.lua `realoptions` lands in the demo);
earlier route runs showed it is English graphics.

# Code / data patches (tools/patches.py)
- Font: lowercase a-z drawn into codes 43-5C of $91:8000 (tools/font.py; outline rule verified on all uppercase).
- Story intro: 4 slot VRAM starts moved from column 8 to 4 (24 columns): imm 0DF257/0DF29E/0DF2E5/0DF32C.
- Ending quotes: start column 5 -> 2 (28 columns): imm 0DEBD1.
- Text relocation: bank-$9B groups -> bank $8F free space; credits -> new bank $B0 (ROM padded to 2 MB, header already
  declared 2 MB). Bank immediates listed in tools/textdefs.py.
