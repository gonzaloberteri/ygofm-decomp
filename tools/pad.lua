-- Scripted controller input for PCSX-Redux.
--
-- Why this exists: a restored save state with no input runs the game's *idle*
-- loop.  Sampling the in-duel state showed 3546 of 3594 samples landing in
-- func_800736C4 -- a 16-instruction spin that is already decompiled -- so the
-- duel's actual logic (summon, attack, fusion) was never measured at all.
-- Pressing buttons is the cheapest way into the code this project most wants to
-- read.
--
-- This is a *separate* -dofile from sample.lua/trace.lua rather than a module
-- they import: both of those already own a GPU::Vsync listener, and Redux is
-- happy to run several scripts, so input stays decoupled from measurement.
--
--     -dofile tools/pad.lua -dofile tools/sample.lua
--
-- Environment:
--   PAD_SCRIPT  comma-separated button names, cycled in order
--   PAD_START   absolute Vsync at which to start pressing (after the state load)
--   PAD_HOLD    frames to hold each button   (default 4)
--   PAD_GAP     frames released between them (default 8)
--
-- The button indices are Redux's, which are the PSX pad's own bit positions --
-- taken from the m_scancodes table in pad.cc, not guessed.  1 and 2 are L3/R3
-- and only exist on an analog pad.
local BUTTONS = {
    select = 0, l3 = 1, r3 = 2, start = 3,
    up = 4, right = 5, down = 6, left = 7,
    l2 = 8, r2 = 9, l1 = 10, r1 = 11,
    triangle = 12, circle = 13, cross = 14, square = 15,
}

-- Cursor movement plus confirm.  Deliberately avoids start and select: in this
-- game they open or leave menus, which can walk the run straight out of the
-- duel that the save state was captured for.
local DEFAULT = 'down,cross,right,cross,up,cross,left,cross'

local function log(msg)
    -- PCSX.log, not print: print goes to the Lua console, which -no-ui has none
    -- of, so the output vanishes and the script looks like it never ran.
    PCSX.log('[pad] ' .. msg)
end

local script = {}
for name in (os.getenv('PAD_SCRIPT') or DEFAULT):gmatch('[^,%s]+') do
    local idx = BUTTONS[name:lower()]
    if idx == nil then
        log('unknown button "' .. name .. '" -- ignored')
    else
        script[#script + 1] = {name = name:lower(), idx = idx}
    end
end

local startAt = tonumber(os.getenv('PAD_START')) or 0
local hold = tonumber(os.getenv('PAD_HOLD')) or 4
local gap = tonumber(os.getenv('PAD_GAP')) or 8

if #script == 0 then
    log('no buttons to press; input driver idle')
    return
end

-- Redux forces buttons by AND-ing the real pad state with an override mask that
-- defaults to 0xffff.  PSX buttons are active low, so clearing a bit forces the
-- button down -- which is why "setOverride" presses and "clearOverride"
-- releases.  It follows that this can only force a press, never force a button
-- to stay up, which is fine here.
--
-- Call these with a dot, not a colon.  Redux reads the button as Lua argument 1,
-- so `pad():setOverride(n)` passes the pad table as argument 1 and fails with
-- "Invalid argument to setOverride" -- silently, since it is inside a pcall.
local function pad()
    return PCSX.SIO0.slots[1].pads[1]
end

local frames = 0
local step = 0          -- how far into the current button's hold+gap window
local cursor = 0        -- index into script, 0-based
local held = nil
local selfChecked = false

log(string.format('%d buttons, hold %d gap %d, starting at frame %d: %s',
                  #script, hold, gap, startAt,
                  (os.getenv('PAD_SCRIPT') or DEFAULT)))

PCSX.Events.createEventListener('GPU::Vsync', function()
    frames = frames + 1
    if frames < startAt then return end

    if step == 0 then
        local entry = script[(cursor % #script) + 1]
        local ok, err = pcall(function() pad().setOverride(entry.idx) end)
        if not ok then
            log('setOverride failed: ' .. tostring(err))
            return
        end
        held = entry
        -- Read the button back once, at the pad layer.  If this says false the
        -- override never took and the bug is here; if it says true the pad is
        -- reporting the press and anything still unchanged is downstream, in how
        -- the game polls.  Worth the one line: a driver that logs presses while
        -- changing nothing looks identical either way.
        if not selfChecked then
            selfChecked = true
            local okc, pressed = pcall(function() return pad().getButton(entry.idx) end)
            log(string.format('self-check: after setOverride(%s) getButton=%s',
                              entry.name, okc and tostring(pressed) or 'ERROR'))
        end
    elseif step == hold and held ~= nil then
        pcall(function() pad().clearOverride(held.idx) end)
        held = nil
    end

    step = step + 1
    if step >= hold + gap then
        step = 0
        cursor = cursor + 1
        if cursor % (#script * 4) == 0 then
            log(string.format('frame %d: %d button presses issued', frames, cursor))
        end
    end
end)
