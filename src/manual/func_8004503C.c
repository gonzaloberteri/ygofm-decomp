/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8004503C {
    /* 0x0000 */ u8  unk0000[0x49];
    /* 0x0049 */ u8  unk0049;
    /* 0x004A */ u8  unk004A[0x4C8];
    /* 0x0512 */ s16 unk0512;
} Unk8004503C;

extern Unk8004503C *D_8009B45C;

void func_8004503C(s32 arg0, s32 arg1)
{
    D_8009B45C->unk0512 = arg0;
    D_8009B45C->unk0049 = arg1;
}
