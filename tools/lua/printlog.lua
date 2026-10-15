-- Runtime text scan: log every string (and every line start) the printer task ($80:B688) prints, once per
-- (pointer, vram): mode ($1C), vram ($1E), attr ($20), pointer and the first 40 bytes.
-- Task structs live in bank $7E (X = task base, DBR = $7E inside tasks).
--   emu.py ... --script tools/lua/printlog.lua
local M = emu.memType.snesMemory
local seen = {}
local function rd16(a) return emu.read(a, M) | (emu.read(a + 1, M) << 8) end
L.on_exec(0x80B6C8, 0x80B6C8, function()
  local x = 0x7E0000 | emu.getState()["cpu.x"]
  local ptr = rd16(0) | (emu.read(2, M) << 16)
  if (ptr & 0xFFFF) ~= 0 and emu.read(ptr - 1, M) > 1 then return end  -- only at string / line start
  local vram = rd16(x + 0x2E)
  local key = string.format("%06X", ptr)
  if seen[key] then return end
  seen[key] = true
  local t = {}
  for i = 0, 39 do
    local b = emu.read(ptr + i, M)
    t[#t + 1] = string.format("%02X", b)
    if b <= 1 then break end
  end
  L.log(string.format("%d mode=%d vram=%04X attr=%04X ptr=%06X %s", L.frame, rd16(x + 0x1C), vram, rd16(x + 0x20),
    ptr, table.concat(t, " ")))
end)
