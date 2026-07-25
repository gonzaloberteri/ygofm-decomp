#include "types.h"
#include "m2c_macros.h"

s32 func_800429BC(void *arg0, void *arg1) {
    return M2C_FIELD(arg0, s32 *, 0x54) + ((M2C_FIELD(arg1, u8 *, 1) << 8) | M2C_FIELD(arg1, u8 *, 0));
}
