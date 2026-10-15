-- Log every LZ decompression ($80:F28D): source block (file offset), dest X in $7F, frame.
local M = emu.memType.snesMemory
L.on_exec(0x80F2AE, 0x80F2AE, function()
  local src = (emu.read(0, M) | emu.read(1, M) << 8 | emu.read(2, M) << 16) - 4
  local off = ((src & 0x7F0000) >> 1) | (src & 0x7FFF)
  L.log(string.format("%d lz src=%06X file=%06X dest=7F%04X", L.frame, src, off, emu.getState()["cpu.x"]))
end)
