"""Build the English ROM (or the identity / marker builds).

    python -X utf8 build.py [--mode en|identity|marker] [--out build/dolucky_en.sfc] [--qa ID=text ...]

en:       English text (`en`), font and code patches. An entry with no `en` keeps its Japanese bytes.
identity: re-encode every `jp` field into its original place: must equal the original ROM (tests/test_identity.py).
marker:   every string replaced by its id + filler at the box limit (width gate / marker tour).
"""
import argparse, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
from textio import EN, JP, ROOT, enc, load_group, read_rom, strings_in  # noqa: E402
from textdefs import FREE, GROUPS, ROM_SIZE, bank_byte, cpu_lo  # noqa: E402


class Alloc:
    def __init__(self, start, end):
        self.pos, self.end, self.start = start, end, start

    def take(self, n):
        if self.pos + n > self.end:
            return None
        p = self.pos; self.pos += n
        return p


def marker_text(e, mx):
    tag = '#' + e['id'].split('_', 1)[1] + ':'
    out = []
    for i, ln in enumerate(e['jp'].split('\n')):
        if not ln.strip():
            out.append(''); continue
        s = (tag if i == 0 else '') + 'The quick brown fox jumps over the lazy dog'
        out.append(s[:mx] if e['form'] != 'credits' else s[:max(len(tag) + 4, len(JP.encode(ln)))])
    return '\n'.join(out)


def entry_bytes(e, mode, pad):
    if mode == 'identity' or (mode == 'en' and not e['en']):
        return enc(JP, e['jp'])
    text = marker_text(e, e.get('max') or 16) if mode == 'marker' else e['en']
    if pad:
        text = '\n'.join(ln.ljust(pad) for ln in text.split('\n'))
    return enc(EN, text)


def group_texts(rom, g, mode, qa):
    """[(key, bytes)] in placement order and {ref offset: key}."""
    entries = [dict(e, max=g['pad'] if 'pad_from' in g and i >= g['pad_from'] else g.get('limit'))
               for i, e in enumerate(load_group(g['id']))]
    refs = [(t + 2 * i) for t, n in g['tables'] for i in range(n)] + list(g['imms'])
    blobs, refkey = [], {}
    if g.get('slots'):
        (t, n), = g['tables']
        assert len(entries) == n, g['id']
        seen = {}
        for i, e in enumerate(entries):
            if e['id'] in qa:
                e = dict(e, en=qa[e['id']])
            b = entry_bytes(e, mode, g.get('pad'))
            if b not in seen:
                seen[b] = len(blobs); blobs.append((len(blobs), b))
            refkey[t + 2 * i] = seen[b]
        return blobs, refkey
    orig = strings_in(rom, *g['region'])
    assert len(orig) == len(entries), g['id']
    for i, ((off, raw), e) in enumerate(zip(orig, entries)):
        assert int(e['addr'], 16) == off, e['id']
        if e['id'] in qa:
            e = dict(e, en=qa[e['id']])
        pad = g.get('pad') if i >= g.get('pad_from', 0) else None
        blobs.append((off, entry_bytes(e, mode, pad)))
    for r in refs:
        v = rom[r] | rom[r + 1] << 8
        hit = [off for off, _ in orig if cpu_lo(off) == v]
        assert len(hit) == 1, (g['id'], hex(r), hex(v))
        refkey[r] = hit[0]
    return blobs, refkey


def place_groups(rom, mode, qa):
    free = {k: Alloc(*v) for k, v in FREE.items()}
    for g in GROUPS:
        blobs, refkey = group_texts(rom, g, mode, qa)
        rs, re_ = g['region']
        rom[rs:re_] = bytes(re_ - rs)
        newaddr = {}
        relocate = mode != 'identity' and g.get('reloc')
        if relocate:
            al = free[g['reloc']]
            for bi in g['bank_imms']:
                assert rom[bi - 1] == 0xA9 and rom[bi + 1] == 0x00, hex(bi)
                rom[bi] = bank_byte(al.start)
            areas = [al]
        else:
            areas = [Alloc(rs, re_)] + [free[s] for s in g.get('spill', [])]
        for key, b in blobs:
            p = None
            for ar in areas:
                p = ar.take(len(b))
                if p is not None:
                    break
            if p is None:
                raise SystemExit('no room for %s string %s (%d bytes)' % (g['id'], key, len(b)))
            rom[p:p + len(b)] = b
            newaddr[key] = p
        for r, key in refkey.items():
            nv = cpu_lo(newaddr[key])
            rom[r] = nv & 0xFF; rom[r + 1] = nv >> 8


def build(mode='en', qa=None):
    rom = bytearray(read_rom())
    if mode != 'identity':
        rom += b'\xFF' * (ROM_SIZE - len(rom))
        import patches
        patches.apply(rom, mode)
    place_groups(rom, mode, qa or {})
    return bytes(rom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='en', choices=['en', 'identity', 'marker'])
    ap.add_argument('--out')
    ap.add_argument('--qa', action='append', default=[], help='ID=text override for one entry (\\n = new line)')
    a = ap.parse_args()
    qa = {k: v.replace('\\n', '\n') for k, v in (s.split('=', 1) for s in a.qa)}
    out = a.out or os.path.join(ROOT, 'build', 'dolucky_%s.sfc' % a.mode)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    data = build(a.mode, qa)
    with open(out, 'wb') as f:
        f.write(data)
    print('built', out)


if __name__ == '__main__':
    main()
