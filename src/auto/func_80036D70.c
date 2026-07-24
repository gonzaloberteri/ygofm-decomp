#include "types.h"
#include "m2c_macros.h"

s32 func_80036D70(void *arg0) {
    void **temp_a0;
    void *temp_a1;

    temp_a0 = arg0 + (M2C_FIELD(arg0, s8 *, 0x58) * 4);
    temp_a1 = *temp_a0;
    *temp_a0 = temp_a1 + 4;
    return (M2C_FIELD(temp_a1, u8 *, 3) << 0x18) | (M2C_FIELD(temp_a1, u8 *, 2) << 0x10) | (M2C_FIELD(temp_a1, u8 *, 1) << 8) | M2C_FIELD(temp_a1, u8 *, 0);
}
