"""Render the 8x16 2bpp font (file 0x88000, $91:8000; char c = tiles 2c (top) and 2c+1 (bottom)) to a PNG sheet.

    python -X utf8 tools/font_sheet.py ROM OUT.png [--at HEX] [--count N] [--zoom 3]
"""
import argparse
from PIL import Image, ImageDraw


def tile2(d, off):
    return [[((d[off + 2 * y] >> (7 - x)) & 1) | (((d[off + 2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)]
            for y in range(8)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom'); ap.add_argument('out')
    ap.add_argument('--at', default='88000'); ap.add_argument('--count', type=int, default=224)
    ap.add_argument('--zoom', type=int, default=3)
    a = ap.parse_args()
    d = open(a.rom, 'rb').read(); base = int(a.at, 16)
    cols = 16; rows = (a.count + cols - 1) // cols
    cw, ch = 12, 26
    im = Image.new('RGB', (cols * cw + 20, rows * ch), (40, 40, 60))
    dr = ImageDraw.Draw(im)
    pal = [(0, 0, 80), (255, 255, 255), (160, 160, 160), (255, 80, 80)]
    for c in range(a.count):
        x0 = 20 + (c % cols) * cw; y0 = (c // cols) * ch + 8
        for half in range(2):
            t = tile2(d, base + c * 32 + half * 16)
            for y in range(8):
                for x in range(8):
                    im.putpixel((x0 + x, y0 + half * 8 + y), pal[t[y][x]])
        if c % cols == 0:
            dr.text((0, y0 + 2), '%02X' % c, fill=(255, 255, 0))
    im = im.resize((im.width * a.zoom, im.height * a.zoom), Image.NEAREST)
    im.save(a.out)


if __name__ == '__main__':
    main()
