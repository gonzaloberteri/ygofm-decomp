/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns,-fno-schedule-insns2 */
#include "types.h"

typedef struct Unk80038BA8 {
    /* 0x00 */ u32 unk00[0x16];
    /* 0x58 */ s8  unk58;
} Unk80038BA8;

extern s32 func_80036D3C(Unk80038BA8 *);

void func_80038BA8(Unk80038BA8 *arg0)
{
    u32 v;
    u32 *p;

    v = func_80036D3C(arg0);
    p = &arg0->unk00[arg0->unk58];
    *p = (*p & 0xFFFF0000) | (v & 0xFFFF);
}
