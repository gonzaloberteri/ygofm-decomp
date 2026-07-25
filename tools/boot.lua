-- Smoke test for verify_boot.py: restore a save state on the rebuilt image and
-- confirm the game keeps running.
--
-- "Keeps running" is measured as Vsyncs delivered, not as "the process is still
-- alive".  A hung emulator stays alive; a hung *game* stops producing frames.
-- The old DuckStation version of this check only tested that the process had
-- not exited, which a black screen or a spinning loop would have passed.
--
-- The state load mirrors trace.lua: boot for a warmup period first, because
-- restoring during BIOS init leaves the emulator with nothing running, and
-- Redux writes slots through ZWriter so the file must be read back via zReader.
local statePath = os.getenv('BOOT_STATE')
local warmup = tonumber(os.getenv('BOOT_WARMUP')) or 120
local limit = tonumber(os.getenv('BOOT_FRAMES')) or 600
local outPath = os.getenv('BOOT_OUT') or 'build/boot/result.txt'

local frames = 0
local phase = (statePath ~= nil and statePath ~= '') and 'boot' or 'run'

local function log(msg)
    -- PCSX.log, not print: print goes to the Lua console, which -no-ui has none
    -- of, so the output vanishes and the script looks like it never ran.
    PCSX.log('[boot] ' .. msg)
end

local function writeResult(reason, ran)
    local f = io.open(outPath, 'w')
    if f == nil then
        log('could not write ' .. outPath)
        return
    end
    f:write(string.format('reason=%s frames=%d\n', reason, ran))
    f:close()
end

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

if phase == 'boot' then
    log(string.format('booting %d frames before restoring the state', warmup))
else
    log(string.format('running %d frames from boot', limit))
end

PCSX.Events.createEventListener('GPU::Vsync', function()
    frames = frames + 1

    if phase == 'boot' then
        if frames >= warmup then
            if not loadState() then
                writeResult('state-load-failed', frames)
                PCSX.quit(1)
                return
            end
            phase = 'run'
            frames = 0
        end
        return
    end

    if frames % 60 == 0 then
        log(string.format('frame %d/%d', frames, limit))
    end
    if frames >= limit then
        -- Reaching the frame limit *is* the pass: the game produced every frame
        -- asked of it after the state was restored.
        writeResult('frame-limit', frames)
        PCSX.quit(0)
    end
end)
