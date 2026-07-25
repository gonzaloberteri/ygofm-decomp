/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Unk8009B45C {
    /* 0x00 */ u8  unk00[0x3C];
    /* 0x3C */ s32 unk3C;
    /* 0x40 */ u16 unk40;
    /* 0x42 */ u8  unk42[8];
    /* 0x4A */ u8  unk4A;
} Unk8009B45C;

extern Unk8009B45C *D_8009B45C;

void func_80046990(s32 arg0, s32 arg1, s32 arg2)
{
    D_8009B45C->unk3C = 0;
    if (arg0 == 0) {
        D_8009B45C->unk4A &= 0xFE;
    }
    if (arg1 == 0) {
        D_8009B45C->unk4A &= 0xFD;
    }
    if (arg2 == 0) {
        D_8009B45C->unk4A &= 0xBF;
    }
    D_8009B45C->unk40 |= 0xA;
}
