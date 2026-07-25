/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800F2C40 {
    u8 unk0000[0xDC0];
    u8 unkDC0;
    u8 unkDC1;
    u8 unkDC2;
    u8 unkDC3;
    u8 unkDC4[0xE20 - 0xDC4];
} Unk800F2C40;

extern Unk800F2C40 D_800F2C40[];

void func_80059590(s32 index, s32 arg1, s32 arg2, s32 arg3, s32 arg4)
{
    Unk800F2C40 *p = &D_800F2C40[index];

    p->unkDC3 = arg1;
    p->unkDC0 = arg2;
    p->unkDC1 = arg3;
    p->unkDC2 = arg4;
}
