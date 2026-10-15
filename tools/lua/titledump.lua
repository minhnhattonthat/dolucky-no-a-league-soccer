-- Dump PPU + screenshot DELAY frames (default 260) after the title scene task $89:82A7 is spawned.
local M = emu.memType.snesMemory
local at
L.on_exec(0x80AA97, 0x80AA97, function()
  if not at and emu.read(0x40, M) == 0xA7 and emu.read(0x41, M) == 0x82 and emu.read(0x42, M) == 0x89 then
    at = L.frame + (DELAY or 260)
  end
end)
L.on_frame(function(f)
  if at and f == at then L.dump_ppu("title"); L.shot("title.png") end
end)
