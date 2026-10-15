"""Non-text ROM patches applied by build.py (font, graphics, code). Listed in docs/re/hooks.md."""
import font

# (file offset of a 16-bit LDA #imm operand, original value, new value)
IMM16 = [
    # story intro: 4 line slots start at column 4 instead of 8 (24 columns instead of 16)
    (0xDF257, 0x0508, 0x0504), (0xDF29E, 0x0568, 0x0564), (0xDF2E5, 0x05C8, 0x05C4), (0xDF32C, 0x0628, 0x0624),
    # ending quotes: start at column 2 instead of 5 (28 columns)
    (0xDEBD1, 0x1A45, 0x1A42),
]


def apply(rom, mode):
    font.patch(rom)  # lowercase a-z in codes 43-5C
    for off, old, new in IMM16:
        assert rom[off - 1] == 0xA9 and rom[off] | rom[off + 1] << 8 == old, hex(off)
        rom[off] = new & 0xFF; rom[off + 1] = new >> 8
