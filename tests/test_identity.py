import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build  # noqa: E402
from textio import JP, dec, enc, load_group, read_rom, strings_in  # noqa: E402
from textdefs import FREE, GROUPS  # noqa: E402


def test_identity_build_is_byte_identical():
    assert build.build('identity') == read_rom()


def test_roundtrip_every_string():
    rom = read_rom()
    for g in GROUPS:
        for off, raw in strings_in(rom, *g['region']):
            text, used = dec(JP, rom, off)
            assert used == len(raw)
            assert enc(JP, text) == raw, (g['id'], hex(off))


def test_extracted_jp_matches_rom():
    rom = read_rom()
    for g in GROUPS:
        for e in load_group(g['id']):
            assert dec(JP, rom, int(e['addr'], 16))[0] == e['jp'], e['id']


def test_free_space_is_empty_in_original():
    rom = read_rom()
    for name, (a, b) in FREE.items():
        assert set(rom[a - 1:b]) == {0}, name
