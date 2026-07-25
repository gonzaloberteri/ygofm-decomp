#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_80019B2C();                            /* static */

void func_80019BA0(void *arg0, s8 arg1, s16 arg2, s16 arg3) {
    M2C_FIELD(arg0, s8 *, 0x6C) = 1;
    M2C_FIELD(arg0, s8 *, 0x21) = arg1;
    M2C_FIELD(arg0, s16 *, 0x28) = arg2;
    M2C_FIELD(arg0, s16 *, 0x2A) = arg3;
    M2C_FIELD(arg0, M2C_UNK (**)(), 0x24) = func_80019B2C;
    M2C_FIELD(arg0, u16 *, 8) = (u16) (M2C_FIELD(arg0, u16 *, 8) | 4);
}
