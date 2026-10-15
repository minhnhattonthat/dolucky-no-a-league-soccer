"""Recon: list every spawn of the text printer task ($80:B688) and the params stored to the new task
($1C mode, $1E vram, $20 attr, $22 delay, $24/$26 text pointer) found in the next 0x60 bytes.

    python -X utf8 tools/find_printer_calls.py ROM
"""
import re, sys

d = open(sys.argv[1], 'rb').read()


def lorom(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


for m in re.finditer(re.escape(b'\xa9\x88\xb6\x85\x40'), d):
    s = m.start(); win = d[s:s + 0x70]
    params = {}
    for mm in re.finditer(rb'\xa9(..)\x99(.)\x00', win, re.S):
        off = mm.group(2)[0]
        if off in (0x1C, 0x1E, 0x20, 0x22, 0x24, 0x26) and off not in params:
            params[off] = int.from_bytes(mm.group(1), 'little')
    bank = s // 0x8000
    ptr = None
    if 0x24 in params:
        b = params.get(0x26, None)
        if b is not None:
            ptr = lorom((b << 16) | params[0x24])
    txt = ''
    if ptr is not None and ptr < len(d):
        e = d.find(b'\x00', ptr)
        txt = d[ptr:min(e, ptr + 40)].hex(' ')
    print('%06X bank%02X %s ptr=%s %s' % (s, bank, ' '.join('%02X=%04X' % (k, v) for k, v in sorted(params.items())),
                                         '%06X' % ptr if ptr is not None else '-', txt))
