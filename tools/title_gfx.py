"""Title subtitle (graphics text): the Japanese title ドラッキーのAりーぐさっかー is 8 OBJ sprites (16x16, 4bpp,
palette 2, y 94, x 72..184) in the LZ block at file 0x6CE1C (decompressed to VRAM $6000 words = byte 0xC000).
We redraw it as "DOLUCKY'S A-LEAGUE SOCCER" in a small outlined pixel font and recompress in place.

    python -X utf8 tools/title_gfx.py render VRAM.bin PAL.bin OUT.png   # strip as the screen shows it (from a dump)
    python -X utf8 tools/title_gfx.py preview OUT.png                    # our English strip (from the built ROM data)
"""
import sys

import lz

BLOCK = 0x6CE1C
BLOCK_USED = 2595          # compressed size in the original ROM (recompressed data must fit)
TILES = [0x62, 0x60, 0x4E, 0x4C, 0x4A, 0x48, 0x46, 0x44]  # left to right
FILL, OUTLINE = 2, 5
TEXT = "DOLUCKY'S A-LEAGUE SOCCER"

GLYPHS = {
    'D': ['###.', '#..#', '#..#', '#..#', '#..#', '#..#', '###.'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'L': ['#...', '#...', '#...', '#...', '#...', '#...', '####'],
    'U': ['#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'C': ['.###', '#...', '#...', '#...', '#...', '#...', '.###'],
    'K': ['#..#', '#.#.', '##..', '##..', '#.#.', '#..#', '#..#'],
    'Y': ['#..#', '#..#', '#..#', '.##.', '.#..', '.#..', '.#..'],
    "'": ['#', '#', '.', '.', '.', '.', '.'],
    'S': ['.###', '#...', '#...', '.##.', '...#', '...#', '###.'],
    'A': ['.##.', '#..#', '#..#', '####', '#..#', '#..#', '#..#'],
    '-': ['...', '...', '...', '###', '...', '...', '...'],
    'E': ['####', '#...', '#...', '###.', '#...', '#...', '####'],
    'G': ['.###', '#...', '#...', '#.##', '#..#', '#..#', '.###'],
    'R': ['###.', '#..#', '#..#', '###.', '#.#.', '#..#', '#..#'],
    ' ': ['..', '..', '..', '..', '..', '..', '..'],
}
ROWMAP = [0, 1, 1, 2, 3, 3, 4, 5, 5, 6]   # 7 design rows -> 10 pixel rows
TOP = 3


def strip():
    """128x16 colour indices of the English subtitle, centred."""
    w = sum(len(GLYPHS[c][0]) + 1 for c in TEXT) - 1
    sk = [[False] * 128 for _ in range(16)]
    x = (128 - w) // 2
    for c in TEXT:
        g = GLYPHS[c]
        for ry, sy in enumerate(ROWMAP):
            for gx, ch in enumerate(g[sy]):
                if ch == '#':
                    sk[TOP + ry][x + gx] = True
        x += len(g[0]) + 1
    out = [[0] * 128 for _ in range(16)]
    for y in range(16):
        for x in range(128):
            if sk[y][x]:
                out[y][x] = FILL
            elif any(0 <= y + dy < 16 and 0 <= x + dx < 128 and sk[y + dy][x + dx]
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                out[y][x] = OUTLINE
    return out


def put_tile4(buf, off, px):
    for y in range(8):
        b = [0, 0, 0, 0]
        for x in range(8):
            v = px[y][x]
            for p in range(4):
                b[p] |= ((v >> p) & 1) << (7 - x)
        buf[off + 2 * y], buf[off + 2 * y + 1], buf[off + 16 + 2 * y], buf[off + 17 + 2 * y] = b


def get_tile4(d, off):
    return [[((d[off + 2 * y] >> (7 - x)) & 1) | (((d[off + 2 * y + 1] >> (7 - x)) & 1) << 1) |
             (((d[off + 16 + 2 * y] >> (7 - x)) & 1) << 2) | (((d[off + 17 + 2 * y] >> (7 - x)) & 1) << 3)
             for x in range(8)] for y in range(8)]


def strip_from(gfx, base=0):
    out = [[0] * 128 for _ in range(16)]
    for i, t in enumerate(TILES):
        for sub, (dx, dy) in enumerate([(0, 0), (8, 0), (0, 8), (8, 8)]):
            p = get_tile4(gfx, base + (t + (sub & 1) + (16 if sub >= 2 else 0)) * 32)
            for y in range(8):
                for x in range(8):
                    out[dy + y][i * 16 + dx + x] = p[y][x]
    return out


def patch(rom):
    raw, used, size = lz.decompress(rom, BLOCK)
    assert used == BLOCK_USED and size == len(raw)
    gfx = bytearray(raw)
    s = strip()
    for i, t in enumerate(TILES):
        for sub, (dx, dy) in enumerate([(0, 0), (8, 0), (0, 8), (8, 8)]):
            px = [[s[dy + y][i * 16 + dx + x] for x in range(8)] for y in range(8)]
            put_tile4(gfx, (t + (sub & 1) + (16 if sub >= 2 else 0)) * 32, px)
    c = lz.compress(bytes(gfx))
    assert len(c) <= BLOCK_USED, len(c)
    rom[BLOCK:BLOCK + BLOCK_USED] = c + bytes(BLOCK_USED - len(c))


def save_png(idx, path, pal=None):
    from PIL import Image
    cols = {0: (0, 0, 0), FILL: (230, 230, 200), OUTLINE: (40, 120, 40)}
    im = Image.new('RGB', (128, 16))
    for y in range(16):
        for x in range(128):
            v = idx[y][x]
            if pal:
                w = pal[2 * (160 + v)] | pal[2 * (160 + v) + 1] << 8
                c = ((w & 31) << 3, ((w >> 5) & 31) << 3, ((w >> 10) & 31) << 3)
            else:
                c = cols.get(v, (255, 0, 255))
            im.putpixel((x, y), c)
    im.resize((128 * 6, 16 * 6), Image.NEAREST).save(path)


if __name__ == '__main__':
    if sys.argv[1] == 'render':
        save_png(strip_from(open(sys.argv[2], 'rb').read(), 0xC000), sys.argv[4], open(sys.argv[3], 'rb').read())
    else:
        save_png(strip(), sys.argv[2])
