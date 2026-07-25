/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8004006C {
    u8  unk00[0x8];
    u16 unk08;
    u8  unk0A[0x66];
} Unk8004006C;

extern Unk8004006C D_800EFE48[];

s32 func_8004006C(void)
{
    Unk8004006C *p;
    s32 i;

    p = D_800EFE48;
    for (i = 0; i < 0x60; i++) {
        if (!(p->unk08 & 0x80)) {
            return i;
        }
        p++;
    }
    return -1;
}
