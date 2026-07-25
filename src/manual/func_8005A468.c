/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

typedef struct Card8005A468 {
    /* 0x0 */ u8 unk0[0xD];
    /* 0xD */ u8 unkD;
} Card8005A468;

typedef struct Duelist8005A468 {
    /* 0x0000 */ u8            unk0000[0x1E0];
    /* 0x01E0 */ Card8005A468 *unk01E0[0x100];
    /* 0x05E0 */ u8            unk05E0[0x83B];
    /* 0x0E1B */ u8            unk0E1B;
    /* 0x0E1C */ u8            unk0E1C[4];
} Duelist8005A468;

extern Duelist8005A468 D_800F2C40[];

void func_8005A468(s32 arg0, s32 arg1)
{
    Duelist8005A468 *d;
    Card8005A468 **p;
    s32 i;

    d = &D_800F2C40[arg0];
    p = d->unk01E0;
    for (i = 0; i < d->unk0E1B; i++) {
        (*p)->unkD = arg1;
        p++;
    }
}
