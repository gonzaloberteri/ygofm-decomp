#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_8008AD50(void *, s32, s32, s32);       /* static */

void func_800134E0(void *arg0, s32 arg1, s32 arg2, s32 arg3) {
    s32 temp_a1;
    s32 temp_a2;
    s32 temp_a3;
    void *temp_a0;

    temp_a0 = arg0 + 0x10;
    temp_a1 = arg1 + M2C_FIELD(temp_a0, s32 *, 0xC);
    M2C_FIELD(arg0, s32 *, 0x10) = temp_a1;
    temp_a2 = arg2 + M2C_FIELD(temp_a0, s32 *, 0x10);
    temp_a3 = arg3 + M2C_FIELD(temp_a0, s32 *, 0x14);
    M2C_FIELD(temp_a0, s32 *, 4) = temp_a2;
    M2C_FIELD(temp_a0, s32 *, 8) = temp_a3;
    func_8008AD50(temp_a0, temp_a1, temp_a2, temp_a3);
}
