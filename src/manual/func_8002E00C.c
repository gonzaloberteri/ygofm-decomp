/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-strength-reduce */
#include "types.h"

typedef struct Chan14 {
    /* 0x00 */ s32 unk_00;
    /* 0x04 */ s16 unk_04;
    /* 0x06 */ u8  unk_06[0x14 - 0x06];
} Chan14;

extern void func_8004036C(s32);

void func_8002E00C(Chan14 *p)
{
    s32 i;

    *(s16 *)((u8 *)p + 0x3C) = -1;
    for (i = 0; i < 3; i++) {
        func_8004036C(p->unk_00);
        p->unk_00 = 0;
        p->unk_04 = 0;
        p++;
    }
}
