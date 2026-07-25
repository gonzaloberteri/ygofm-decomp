#include "types.h"
#include "m2c_macros.h"

extern s32 D_8009B400;

M2C_UNK func_80047314(s32);                         /* static */

void func_8003FF08(s32 arg0) {
    s32 temp_s0;

    temp_s0 = arg0 | 0x7000;
    func_80047314(temp_s0 & 0xFFFF);
    D_8009B400 = temp_s0;
}
