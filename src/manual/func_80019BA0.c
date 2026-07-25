/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80019BA0 {
    /* 0x00 */ u8  unk00[0x8];
    /* 0x08 */ u16 unk08;
    /* 0x0A */ u8  unk0A[0x17];
    /* 0x21 */ u8  unk21;
    /* 0x22 */ u8  unk22[0x2];
    /* 0x24 */ void *unk24;
    /* 0x28 */ s16 unk28;
    /* 0x2A */ s16 unk2A;
    /* 0x2C */ u8  unk2C[0x40];
    /* 0x6C */ u8  unk6C;
} Unk80019BA0;

extern u8 D_80019B2C[];

void func_80019BA0(Unk80019BA0 *arg0, s32 arg1, s32 arg2, s32 arg3)
{
    arg0->unk6C = 1;
    arg0->unk21 = arg1;
    arg0->unk28 = arg2;
    arg0->unk2A = arg3;
    arg0->unk24 = D_80019B2C;
    arg0->unk08 |= 4;
}
