/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Unk80058FB0 {
    u8  unk000[0xDD0];
    u16 unkDD0;
    u16 unkDD2;
    u16 unkDD4;
    u16 unkDD6;
    u8  unkDD8[0xE20 - 0xDD8];
} Unk80058FB0;

extern Unk80058FB0 D_800F2C40[];

void func_80058FB0(s32 arg0, u16 *arg1)
{
    Unk80058FB0 *p = &D_800F2C40[arg0];

    arg1[0] = p->unkDD0;
    arg1[1] = p->unkDD2;
    arg1[2] = p->unkDD4;
    arg1[3] = p->unkDD6;
}
