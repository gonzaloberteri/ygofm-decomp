-- PC sampler for PCSX-Redux.
--
-- Breakpoint-based tracing works but does not scale: 1206 execution breakpoints
-- slowed the interpreter enough that 45 minutes reached only frame 400, barely
-- past the game's entry point. Sampling needs no breakpoints, so it runs under
-- the x86-64 dynarec at full speed.
--
-- It answers a different and arguably better question. Breakpoint coverage says
-- "did this function ever run"; sampling says "how much time is spent here",
-- which is what should actually order decompilation work.
--
-- The sample rate is one per Vsync (60/s), which is sparse -- treat the result as
-- a ranking of hot code, not as coverage. A function absent from the samples has
-- not been shown to be unused.

local FUNCS_IN = 'build/trace/funcs.txt'
local OUT = os.getenv('SAMPLE_OUT') or 'build/trace/samples.txt'

local starts = {}          -- sorted function start addresses
local names = {}
local counts = {}
local frames = 0
local limit = tonumber(os.getenv('SAMPLE_FRAMES')) or 3600
local taken = 0
local outside = 0
local done = false

local function log(msg) PCSX.log('[sample] ' .. msg) end

local function load_functions()
    local f = io.open(FUNCS_IN, 'r')
    if not f then
        log('missing ' .. FUNCS_IN)
        return false
    end
    for line in f:lines() do
        local hex, name = line:match('^%s*([0-9A-Fa-f]+)%s+(%S+)')
        if hex then
            local a = tonumber(hex, 16)
            starts[#starts + 1] = a
            names[a] = name
            counts[a] = 0
        end
    end
    f:close()
    table.sort(starts)
    log(string.format('loaded %d function ranges', #starts))
    return #starts > 0
end

-- Binary search for the function containing pc: the last start <= pc.
local function owner(pc)
    local lo, hi = 1, #starts
    if hi == 0 or pc < starts[1] then return nil end
    while lo < hi do
        local mid = math.floor((lo + hi + 1) / 2)
        if starts[mid] <= pc then lo = mid else hi = mid - 1 end
    end
    return starts[lo]
end

-- Checkpointed, not written once at the end: a run that overshoots its timeout
-- is normal, and losing thousands of frames of samples to that made every run an
-- all-or-nothing bet.
local function writeResults(final)
    if done then return end
    if final then done = true end
    local f = io.open(OUT, 'w')
    if not f then log('could not write ' .. OUT) return end
    f:write(string.format('# frames=%d samples=%d outside=%d\n',
                          frames, taken, outside))
    local hit = {}
    for a, c in pairs(counts) do
        if c > 0 then hit[#hit + 1] = a end
    end
    table.sort(hit)                      -- stable, diffable between runs
    for _, a in ipairs(hit) do
        f:write(string.format('%08X %d %s\n', a, counts[a], names[a]))
    end
    f:close()
    log(string.format('%d samples over %d frames, %d distinct functions',
                      taken, frames, #hit))
end

-- Optional: sample the duel instead of the boot path.  Redux writes its slots
-- through ZWriter, so the file is deflate-compressed and has to be read back
-- through zReader.  The state is restored after a warmup rather than at script
-- load, because at load time the emulator has not started and there is nothing
-- to restore into.
local statePath = os.getenv('SAMPLE_STATE')
local warmup = tonumber(os.getenv('SAMPLE_WARMUP')) or 600

local function loadState()
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

if load_functions() then
    local regs = PCSX.getRegisters()
    local booting = statePath ~= nil and statePath ~= ''
    if booting then
        log(string.format('booting %d frames before restoring the state', warmup))
    end
    PCSX.Events.createEventListener('GPU::Vsync', function()
        if booting then
            frames = frames + 1
            if frames >= warmup then
                if not loadState() then PCSX.quit(1) return end
                booting = false
                frames = 0
                log('sampling the restored state until frame ' .. limit)
            end
            return
        end
        frames = frames + 1
        local pc = tonumber(regs.pc)
        if pc then
            local a = owner(pc)
            if a and counts[a] ~= nil then
                counts[a] = counts[a] + 1
                taken = taken + 1
            else
                outside = outside + 1     -- BIOS, SDK, or data
            end
        end
        if frames % 600 == 0 then
            log(string.format('frame %d: %d samples in game code', frames, taken))
            writeResults(false)
        end
        if frames >= limit then
            writeResults(true)
            PCSX.quit(0)
        end
    end)
    log('sampling until frame ' .. limit)
end
