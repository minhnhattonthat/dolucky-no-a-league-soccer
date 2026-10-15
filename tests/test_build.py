import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build  # noqa: E402
import patches, title_gfx, font  # noqa: E402
from textio import read_rom  # noqa: E402
from textdefs import FREE, GROUPS  # noqa: E402


def allowed_ranges():
    r = []
    for g in GROUPS:
        r.append(g['region'])
        r += [(t, t + 2 * n) for t, n in g['tables']]
        r += [(i, i + 2) for i in g['imms']]
        r += [(b, b + 1) for b in g.get('bank_imms', [])]
    r += list(FREE.values())
    r.append((font.FONT + 0x43 * 32, font.FONT + 0x5D * 32))
    r.append((title_gfx.BLOCK, title_gfx.BLOCK + title_gfx.BLOCK_USED))
    r += [(o, o + 2) for o, _, _ in patches.IMM16]
    return r


def test_en_build_writes_only_allowed_ranges():
    orig = read_rom()
    new = build.build('en')
    assert len(new) == 0x200000
    rs = allowed_ranges()
    exp = new[len(orig):]
    assert all(any(a <= len(orig) + i < b for a, b in rs) or v == 0xFF for i, v in enumerate(exp))
    bad = [i for i in range(len(orig)) if orig[i] != new[i] and not any(a <= i < b for a, b in rs)]
    assert not bad, ['%X' % i for i in bad[:20]]


def test_marker_build_fits():
    build.build('marker')


def test_lowercase_outline_rule_matches_uppercase():
    rom = read_rom()
    for c in list(range(0x23, 0x3D)) + list(range(0x73, 0xA0)):
        pix = font.decode(rom[font.FONT + c * 32:font.FONT + c * 32 + 32])
        assert font.render(font.skeleton_of(pix)) == pix


def test_lz_roundtrip_title_block():
    import lz
    raw, used, size = lz.decompress(read_rom(), title_gfx.BLOCK)
    assert lz.decompress(lz.compress(raw), 0)[0] == raw
