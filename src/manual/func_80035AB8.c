/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Sprite80035AB8 {
    /* 0x00 */ u8  unk00[0x3C];
    /* 0x3C */ s16 unk3C;
    /* 0x3E */ s16 unk3E;
    /* 0x40 */ s16 unk40;
    /* 0x42 */ s16 unk42;
    /* 0x44 */ u8  unk44[0x20];
} Sprite80035AB8;

extern Sprite80035AB8 D_800EB0F8[];

void func_80035AB8(s32 idx, s16 arg1, s16 arg2, s16 arg3, s32 arg4)
{
    Sprite80035AB8 *s = &D_800EB0F8[idx];

    s->unk3C = arg1;
    s->unk40 = arg2;
    s->unk3E = arg3;
    s->unk42 = arg4;
}
