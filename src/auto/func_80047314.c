#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B45C;

M2C_UNK func_8004733C(s32, u8);                     /* static */

void func_80047314(s32 arg0) {
    func_8004733C(arg0 & 0xFFFF, M2C_FIELD(D_8009B45C, u8 *, 0x164B));
}
