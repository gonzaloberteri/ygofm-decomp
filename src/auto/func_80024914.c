#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_8004036C(s32);                         /* static */

void func_80024914(void *arg0) {
    s32 temp_a0;

    temp_a0 = M2C_FIELD(arg0, s32 *, 0);
    M2C_FIELD(arg0, u16 *, 0x16) = (u16) (M2C_FIELD(arg0, u16 *, 0x16) & 0x7FFF);
    if (temp_a0 != 0) {
        func_8004036C(temp_a0);
        M2C_FIELD(arg0, s32 *, 0) = 0;
    }
}
