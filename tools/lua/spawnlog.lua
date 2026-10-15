-- Recon: log every task spawn / scene call (JSL $80AA97, $80ABA9, $80AC0C, $80AEA0) with the task pointer in $40/$42.
--   emu.py ... --script tools/lua/spawnlog.lua
local seen = {}
for _, a in ipairs({0x80AA97, 0x80ABA9, 0x80AC0C, 0x80AEA0}) do
  L.on_exec(a, a, function()
    local lo = emu.read(0x40, emu.memType.snesMemory) | (emu.read(0x41, emu.memType.snesMemory) << 8)
    local bk = emu.read(0x42, emu.memType.snesMemory)
    local key = string.format("%06X %02X:%04X", a, bk, lo)
    if not seen[key] then
      seen[key] = true
      L.log(string.format("%d %s", L.frame, key))
    end
  end)
end
