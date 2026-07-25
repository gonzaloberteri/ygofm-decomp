#include "types.h"
#include "m2c_macros.h"

void func_8006C330(void *arg0, void *arg1, void *arg2) {
    M2C_FIELD(arg0, s8 *, 0) = (s8) ((s32) (M2C_FIELD(arg1, u8 *, 0) + M2C_FIELD(arg2, u8 *, 0)) >> 1);
    M2C_FIELD(arg0, s8 *, 1) = (s8) ((s32) (M2C_FIELD(arg1, u8 *, 1) + M2C_FIELD(arg2, u8 *, 1)) >> 1);
    M2C_FIELD(arg0, s8 *, 2) = (s8) ((s32) (M2C_FIELD(arg1, u8 *, 2) + M2C_FIELD(arg2, u8 *, 2)) >> 1);
}
