-- Debug warp (phase 2): boot cold and land on a scene. Scene list: tools/debug/scenes.py (drives this file).
--   emu.py ROM --script tools/debug/warp.lua --var "SCENE='story'" [--var TEAM=0] [--var LEVEL=4] ...
-- Mechanisms (docs/re/debug.md):
--   attract scenes: $10EA = attract slot (1 story, 3 profiles, 6 E9E3), $10E8 = idle timer at the title.
--   bonus: $10AC = 1 (the mode-select code) then OPTION.  debug: OPTION's spawn $85:F1D6 is swapped for $85:ED52.
--   endings: the main sequencer at $80:80E4 is redirected to $80:8297 (tour cleared), $1022 = CPU level.
local M = emu.memType.snesMemory
local function w16(a, v) emu.write(a, v & 0xFF, M); emu.write(a + 1, (v >> 8) & 0xFF, M) end
local function r16(a) return emu.read(a, M) | (emu.read(a + 1, M) << 8) end
local scene = SCENE or "title"

if scene == "story" or scene == "profiles" or scene == "attract6" then
  local slot = ({ story = 1, profiles = 3, attract6 = 6 })[scene]
  L.on_frame(function(f) if f < 600 then w16(0x7E10EA, slot) end end)
end

local function redirect(pc, fn)  -- first pass of the main sequencer ($80:80E4): jump to pc
  local done = false
  L.on_exec(0x8080E4, 0x8080E4, function()
    if done then return end
    done = true
    if fn then fn() end
    local s = emu.getState(); s["cpu.pc"] = pc; emu.setState(s)
  end)
end

if scene == "options" or scene == "bonus" or scene == "debug" then
  redirect(0x8129, function() if scene ~= "options" then w16(0x7E10AC, 1) end end)  -- $80:8129 spawns OPTION
end

if scene == "debug" then
  L.on_exec(0x80AA97, 0x80AA97, function()
    if r16(0x40) == 0xF1D6 and emu.read(0x42, M) == 0x85 then w16(0x40, 0xED52) end
  end)
end

if scene == "profiles" and PROFILE then  -- $9B:F770 stores the random character index
  L.on_exec(0x9BF770, 0x9BF770, function() local s = emu.getState(); s["cpu.a"] = PROFILE; emu.setState(s) end)
end

if scene:match("^ending") then
  local level = LEVEL or ({ ending_easy = 0, ending_normal = 2, ending_true = 4 })[scene] or 4
  local done = false
  L.on_exec(0x8080E4, 0x8080E4, function()
    if done then return end
    done = true
    w16(0x7E1022, level)
    w16(0x7E0FD8, 4)
    w16(0x7E0FCA, 0)          -- player side 1: team = $0F9E (ending code at $9B:DA64)
    w16(0x7E0F9E, TEAM or 0)  -- 0 Doluckys, 1 Funky Dogs, 2 Rabbit Rockers, 3 Wild Bears
    local s = emu.getState()
    s["cpu.pc"] = 0x8297
    emu.setState(s)
    L.log("warp ending level " .. level)
  end)
end
