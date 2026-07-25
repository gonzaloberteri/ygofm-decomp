/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

typedef struct Unk801D0200 {
    /* 0x0000 */ u8  bytes[0x5BC];
    /* 0x05BC */ u16 hist[16];
} Unk801D0200;

extern Unk801D0200 D_801D0200;

void func_80021894(s32 arg0)
{
    u16 *h;
    u16 *q;
    s32 v;
    s32 i;

    v = D_801D0200.bytes[arg0 + 0x4F] + 1;
    D_801D0200.bytes[arg0 + 0x4F] = v;
    if ((u8)v >= 0xFB) {
        D_801D0200.bytes[arg0 + 0x4F] = 0xFA;
    }
    h = D_801D0200.hist;
    i = 0xE;
    q = &h[14];
    while (i >= 0) {
        q[1] = q[0];
        q--;
        i--;
    }
    h[0] = arg0;
}
