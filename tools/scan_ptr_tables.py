"""Recon: find 16-bit in-bank pointer tables whose targets are 00-terminated strings holding kana codes.

    python -X utf8 tools/scan_ptr_tables.py ROM [--min 2]
"""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('rom'); ap.add_argument('--min', type=int, default=2)
ap.add_argument('--stride', type=int, default=2)
a = ap.parse_args()
d = open(a.rom, 'rb').read()


def is_text(off):
    if off == 0 or d[off - 1] != 0:
        return False
    e = d.find(b'\x00', off)
    if e < 0 or e - off > 400 or e == off:
        return False
    s = d[off:e]
    kana = sum(1 for b in s if 0x60 <= b <= 0xD6)
    bad = sum(1 for b in s if b > 0xD6 or 0x41 <= b <= 0x5B)
    return kana >= 2 and bad == 0


for bank in range(len(d) // 0x8000):
    base = bank * 0x8000
    i = base
    while i < base + 0x8000 - 1:
        n = 0; j = i
        while j < base + 0x8000 - 1:
            p = d[j] | d[j + 1] << 8
            if p < 0x8000 or not is_text(base + (p & 0x7FFF)):
                break
            n += 1; j += a.stride
        if n >= a.min:
            tg = [base + ((d[k] | d[k + 1] << 8) & 0x7FFF) for k in range(i, j, a.stride)]
            print('table %06X n=%d -> %s' % (i, n, ' '.join('%06X' % t for t in tg)))
            i = j
        else:
            i += 1
