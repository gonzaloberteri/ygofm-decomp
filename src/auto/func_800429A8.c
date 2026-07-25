#include "types.h"
#include "m2c_macros.h"

s32 func_800429A8(void *arg0) {
    return (M2C_FIELD(arg0, u8 *, 1) << 8) | M2C_FIELD(arg0, u8 *, 0);
}
