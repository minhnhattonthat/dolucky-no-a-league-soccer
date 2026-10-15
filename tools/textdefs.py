"""Text groups of Dolucky no A.League Soccer (Japan) (LoROM). All text is 00-terminated, 01 = new line, printed
by the printer task $80:B688 with the 8x16 font at $91:8000 (docs/re/text.md).

Each group: the strings in one contiguous region `region` (file offsets, [start, end)), their in-bank 16-bit
references (`tables`: (file offset, count) of pointer words; `imms`: file offsets of LDA #imm operands) and how the
build may place them: `spill` lists extra free ranges in the same bank; `reloc` moves every string of the group to
another bank, rewriting the bank immediates `bank_imms` (operand file offsets of LDA #$00bb).
`pad`: English strings are space-padded to this many characters (fixed-width fields).
"""

# free space (file offsets), checked empty in the original ROM by tests/test_free.py
FREE = {
    'bank02': (0x17C4B + 1, 0x18000),   # keep one 00 after the last original byte
    'bank05': (0x2F779 + 1, 0x30000),
    'bank0F': (0x7E18C + 1, 0x80000),
}

GROUPS = [
    dict(id='credits', region=(0x2DEAE, 0x2ED52), imms=[0x2DDA6, 0x2DDB4], tables=[],
         spill=['bank05'], form='credits', limit=28),
    dict(id='debug', region=(0x2F16F, 0x2F1D6), imms=[0x2EE3F, 0x2EE72], tables=[(0x2F159, 11)],
         spill=['bank05'], form='menu', limit=17, pad_from=2, pad=9),
    dict(id='bonus', region=(0x2F693, 0x2F6EA), imms=[0x2F2CE, 0x2F301], tables=[(0x2F67D, 11)],
         spill=['bank05'], form='menu', limit=17, pad_from=2, pad=9),
    dict(id='names', region=(0x12381, 0x12499), imms=[], tables=[(0x12331, 40)],
         spill=['bank02'], form='name', limit=8, pad=8),
    dict(id='endmsg', region=(0x0DE20A, 0x0DE250), imms=[0x0DE150], tables=[],
         reloc='bank0F', bank_imms=[0x0DE156], form='narration', limit=24),
    dict(id='quotes', region=(0x0DED6B, 0x0DF0DE), imms=[], tables=[(0x0DED2F, 30)],
         reloc='bank0F', bank_imms=[0x0DEBE7], form='dlg', limit=28),
    dict(id='story', region=(0x0DF42F, 0x0DF5FA), imms=[], tables=[(0x0DF3E7, 36)],
         reloc='bank0F', bank_imms=[0x0DF26E, 0x0DF2B5, 0x0DF2FC, 0x0DF343], form='narration', limit=24, pad=24, slots=True),
    dict(id='profiles', region=(0x0DFA1C, 0x0DFE17), imms=[], tables=[(0x0DF9F2, 21)],
         reloc='bank0F', bank_imms=[0x0DF919, 0x0DF961, 0x0DF9BE], form='narration', limit=17),
]


def bank_base(off):
    return off & ~0x7FFF


def cpu_lo(off):
    return (off & 0x7FFF) | 0x8000


def bank_byte(off):
    return 0x80 | (off >> 15)
