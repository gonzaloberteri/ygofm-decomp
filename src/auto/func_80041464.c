#include "types.h"
#include "m2c_macros.h"

s32 func_80041464(void *arg0, void *arg1);          /* static */

s32 func_80041464(void *arg0, void *arg1) {
    M2C_FIELD(arg0, s16 *, 0x58) = 0;
    M2C_FIELD(arg0, s32 *, 4) = (s32) (M2C_FIELD(arg0, s32 *, 4) ^ 0x800000);
    M2C_FIELD(arg0, s32 *, 0x50) = (s32) (M2C_FIELD(arg0, s32 *, 0x54) + ((M2C_FIELD(arg1, u8 *, 1) << 8) | M2C_FIELD(arg1, u8 *, 0)));
    return 1;
}
