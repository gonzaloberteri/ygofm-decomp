#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_800472A8(u32);                         /* static */
M2C_UNK func_80047AD0(s32);                         /* static */

void func_80047278(u32 arg0) {
    func_800472A8(arg0 >> 0x10);
    func_80047AD0(arg0 & 0xFFFF);
}
