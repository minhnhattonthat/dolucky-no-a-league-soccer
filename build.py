"""Build the English ROM (or the identity / marker builds).

    python -X utf8 build.py [--mode en|identity|marker] [--out build/dolucky_en.sfc] [--qa ID=text ...]

en:       English text (`en`), font and graphics patches. An entry with no `en` keeps its Japanese bytes.
identity: re-encode every `jp` field into its original place: must equal the original ROM (tests/test_identity.py).
marker:   every string replaced by its id + filler at the box limit (width gate / marker tour).
"""
import argparse, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))
from textio import EN, JP, ROOT, enc, load_group, read_rom, strings_in  # noqa: E402
from textdefs import FREE, GROUPS, bank_byte, cpu_lo  # noqa: E402


class Alloc:
    def __init__(self, start, end):
        self.pos, self.end, self.start = start, end, start

    def take(self, n, what):
        if self.pos + n > self.end:
            return None
        p = self.pos; self.pos += n
        return p


def fit_text(e, mode):
    if mode == 'identity' or (mode == 'en' and not e['en']):
        return enc(JP, e['jp'])
    if mode == 'marker':
        lines = e['jp'].split('\n')
        mx = e.get('max') or 16
        tag = '[' + e['id'].split('_', 1)[1] + ']'
        out = []
        for i, ln in enumerate(lines):
            if not ln.strip():
                out.append(ln); continue
            s = (tag if i == 0 else '') + 'The quick brown fox jumps over the lazy dog'
            out.append(s[:mx])
        return enc(EN, '\n'.join(out))
    text = e['en']
    if e.get('pad'):
        text = text.ljust(e['pad'])
    return enc(EN, text)


def place_groups(rom, mode, qa):
    free = {k: Alloc(*v) for k, v in FREE.items()}
    for g in GROUPS:
        entries = load_group(g['id'])
        orig = strings_in(rom, *g['region'])
        assert len(orig) == len(entries), g['id']
        blobs = []
        for (off, raw), e in zip(orig, entries):
            assert int(e['addr'], 16) == off, e['id']
            if g.get('pad'):
                e = dict(e, pad=g['pad'])
            if e['id'] in qa:
                e = dict(e, en=qa[e['id']])
            b = fit_text(e, mode)
            blobs.append((off, b))
        relocate = mode != 'identity' and g.get('reloc')
        newaddr = {}
        if relocate:
            al = free[g['reloc']]
            for off, b in blobs:
                p = al.take(len(b), g['id'])
                if p is None:
                    raise SystemExit('free space %s full placing %s' % (g['reloc'], g['id']))
                newaddr[off] = p
            for bi in g['bank_imms']:
                assert rom[bi - 1] == 0xA9 and rom[bi + 1] == 0x00, hex(bi)
                rom[bi] = bank_byte(al.start)
            rom[g['region'][0]:g['region'][1]] = bytes(g['region'][1] - g['region'][0])
        else:
            reg = Alloc(*g['region'])
            spills = [free[s] for s in g.get('spill', [])]
            rom[g['region'][0]:g['region'][1]] = bytes(g['region'][1] - g['region'][0])
            for off, b in blobs:
                p = reg.take(len(b), g['id'])
                for sp in spills:
                    if p is not None:
                        break
                    p = sp.take(len(b), g['id'])
                if p is None:
                    raise SystemExit('no room for %s string at %X' % (g['id'], off))
                newaddr[off] = p
        for off, b in blobs:
            p = newaddr[off]
            rom[p:p + len(b)] = b
        # rewrite references
        refs = [(t + 2 * i) for t, n in g['tables'] for i in range(n)] + list(g['imms'])
        for r in refs:
            v = rom[r] | rom[r + 1] << 8
            hit = [o for o in newaddr if cpu_lo(o) == v]
            assert len(hit) == 1, (g['id'], hex(r), hex(v))
            nv = cpu_lo(newaddr[hit[0]])
            rom[r] = nv & 0xFF; rom[r + 1] = nv >> 8


def build(mode='en', qa=None):
    rom = bytearray(read_rom())
    if mode != 'identity':
        import patches
        patches.apply(rom, mode)
    place_groups(rom, mode, qa or {})
    return bytes(rom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='en', choices=['en', 'identity', 'marker'])
    ap.add_argument('--out')
    ap.add_argument('--qa', action='append', default=[], help='ID=text override for one entry')
    a = ap.parse_args()
    qa = dict(s.split('=', 1) for s in a.qa)
    out = a.out or os.path.join(ROOT, 'build', 'dolucky_%s.sfc' % a.mode)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    data = build(a.mode, qa)
    with open(out, 'wb') as f:
        f.write(data)
    print('built', out)


if __name__ == '__main__':
    main()
