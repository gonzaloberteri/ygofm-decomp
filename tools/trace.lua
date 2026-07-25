-- Execution tracer for PCSX-Redux.
--
-- Records which of the game's functions actually execute, so decompilation can
-- target code that runs rather than whatever happens to be small or early in
-- address order.  Function choice has so far been driven by size and address,
-- with no evidence about which functions the boot path even calls.
--
-- Reads addresses from build/trace/funcs.txt, sets an execution breakpoint on
-- each, and records the first hit.
--
-- Invoked by tools/trace.py; see there for the required flags (-run, a real
-- BIOS, and stdin held open).

local ffi = require 'ffi'

-- Raw FFI rather than PCSX.addBreakpoint, because that wrapper does an
-- `ffi.cast` per breakpoint and LuaJIT allows only ~1024 live FFI callbacks.
-- 1200+ breakpoints therefore failed with "too many callbacks" -- and because
-- -dofile swallows load errors, it failed completely silently. One shared
-- callback works because the callback already receives the address.
local C = ffi.load 'PCSX'
local BP_EXEC = 0        -- enum BreakpointType { Exec, Read, Write }

local FUNCS_IN = 'build/trace/funcs.txt'
local HITS_OUT = os.getenv('TRACE_HITS') or 'build/trace/hits.txt'

local frames = 0
-- From the environment, not a global: main.cc runs every -dofile *before* any
-- -exec, so a global set by -exec is still nil when this script reads it.
local limit = tonumber(os.getenv('TRACE_FRAMES')) or 1800   -- ~30 s at 60 Hz
local hits = {}
local order = {}
local nhits = 0
local handles = {}
local nfuncs = 0
local done = false

local function log(msg)
    -- PCSX.log, not print: print goes to the Lua console, which -no-ui has none
    -- of, so output vanished and the script looked like it had never run.
    PCSX.log('[trace] ' .. msg)
end

-- Must return false, or the emulator pauses on every hit and never advances.
local shared_cb = ffi.cast('bool (*)(uint32_t, unsigned, const char*)',
    function(address, _width, _cause)
        local a = tonumber(address)
        if not hits[a] then
            hits[a] = frames
            order[#order + 1] = a
            nhits = nhits + 1
            local h = handles[a]
            if h ~= nil then
                C.removeBreakpoint(h)      -- coverage is a set; once is enough
                handles[a] = nil
            end
        end
        return false
    end)

-- Checkpointed, not written once at the end.  Under the interpreter with every
-- function breakpointed a frame costs seconds, so a run that overshoots its
-- timeout is the normal case rather than the exception -- and losing the whole
-- trace to that would make every run an all-or-nothing bet.
local function writeResults(reason)
    if done then return end
    if reason ~= 'checkpoint' then done = true end
    local f = io.open(HITS_OUT, 'w')
    if not f then
        log('could not write ' .. HITS_OUT)
        return
    end
    f:write(string.format('# reason=%s frames=%d hit=%d of=%d\n',
                          reason, frames, nhits, nfuncs))
    table.sort(order)                       -- stable output, diffable run to run
    for _, a in ipairs(order) do
        f:write(string.format('%08X %d\n', a, hits[a]))
    end
    f:close()
    log(string.format('%s: %d/%d functions executed over %d frames',
                      reason, nhits, nfuncs, frames))
end

local function armBreakpoints()
    local f = io.open(FUNCS_IN, 'r')
    if not f then
        log('missing ' .. FUNCS_IN .. ' -- run tools/trace.py, not this directly')
        return false
    end
    for line in f:lines() do
        local hex = line:match('^%s*([0-9A-Fa-f]+)')
        if hex then
            local addr = tonumber(hex, 16)
            if addr and not handles[addr] then
                handles[addr] = C.addBreakpoint(addr, BP_EXEC, 4, 'trace',
                                                shared_cb, 'trace')
                nfuncs = nfuncs + 1
            end
        end
    end
    f:close()
    log(string.format('armed %d execution breakpoints with one shared callback',
                      nfuncs))
    return nfuncs > 0
end

-- Optional: start from a save state instead of from boot.  Coverage of the duel
-- path is otherwise unreachable -- the boot path never enters a duel on its own,
-- and under the interpreter, which is the only mode that observes breakpoints,
-- there are nowhere near enough frames to navigate there even if it could.
--
-- Redux writes its slots through ZWriter, so the file is deflate-compressed and
-- has to be read back through zReader; handing the raw file to loadSaveState
-- fails.
local statePath = os.getenv('TRACE_STATE')

local function loadState()
    if statePath == nil or statePath == '' then return true end
    local ok, err = pcall(function()
        local f = Support.File.open(statePath, 'READ')
        if f == nil then error('could not open ' .. statePath) end
        PCSX.loadSaveState(Support.File.zReader(f))
    end)
    if not ok then
        log('save state load FAILED: ' .. tostring(err))
        return false
    end
    log('loaded save state ' .. statePath)
    return true
end

-- Three phases, in this order for two independent reasons.
--
-- The state must not be restored during BIOS init.  Loading it on the very
-- first Vsync -- while the log still reads "KERNEL SETUP!" -- left the emulator
-- with nothing running and no further Vsync ever arrived.
--
-- And the breakpoints must not be armed until after that.  Under the
-- interpreter each armed breakpoint costs time on every instruction, so arming
-- them up front means paying for 1206 of them through an entire boot that is
-- about to be thrown away by the state load anyway.
local warmup = tonumber(os.getenv('TRACE_WARMUP')) or 120
local phase = statePath ~= nil and statePath ~= '' and 'boot' or 'trace'

if phase == 'trace' and not armBreakpoints() then
    log('nothing to trace')
else
    if phase == 'boot' then
        log(string.format('booting %d frames before restoring the state', warmup))
    end
    PCSX.Events.createEventListener('GPU::Vsync', function()
        frames = frames + 1

        if phase == 'boot' then
            if frames >= warmup then
                if not loadState() then
                    writeResults('state-load-failed')
                    PCSX.quit(1)
                    return
                end
                phase = 'settle'
                frames = 0
            end
            return
        end

        if phase == 'settle' then
            -- Give the restored state a few frames to run before measuring, so
            -- the first frame after a load is not mistaken for normal play.
            if frames >= 10 then
                if not armBreakpoints() then
                    writeResults('no-breakpoints')
                    PCSX.quit(1)
                    return
                end
                phase = 'trace'
                frames = 0
                log('tracing until frame ' .. limit)
            end
            return
        end

        if frames % 10 == 0 then
            log(string.format('frame %d: %d/%d hit', frames, nhits, nfuncs))
            writeResults('checkpoint')
        end
        if frames >= limit then
            writeResults('frame-limit')
            PCSX.quit(0)
        end
    end)
end
