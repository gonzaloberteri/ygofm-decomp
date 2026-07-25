/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-strength-reduce */
#include "types.h"

extern u8 D_801D0250[];
extern u16 D_801D0200[];

extern void func_8002CCE4(s32);

void func_8002BF3C(void)
{
    u8 *p;
    u16 *q;
    s32 i;

    p = D_801D0250;
    for (i = 0; i < 0x2D2; i++) {
        if (*p != 0) {
            func_8002CCE4(i + 0x121);
        }
        p++;
    }
    q = D_801D0200;
    for (i = 0; i < 0x28; i++) {
        if (*q != 0) {
            func_8002CCE4(*q + 0x120);
        }
        q++;
    }
}
