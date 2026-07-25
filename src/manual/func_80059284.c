/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Duelist {
    u8 unk000[0xE11];
    u8 unkE11;
    u8 unkE12[0xE];
} Duelist;

extern Duelist D_800F2C40[];

void func_80059284(s32 arg0, u8 arg1)
{
    arg0[D_800F2C40].unkE11 = arg1;
}
