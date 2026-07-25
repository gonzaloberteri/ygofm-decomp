/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Rec80033998 {
    /* 0x0 */ u8 unk00[0xD];
    /* 0xD */ u8 unk0D;
    /* 0xE */ u8 unk0E[2];
} Rec80033998;

typedef struct Unk8009B2FC {
    /* 0x0000 */ u8          unk0000[0x2D50];
    /* 0x2D50 */ Rec80033998 recs[0x28];
} Unk8009B2FC;

extern Unk8009B2FC *D_8009B2FC;

s32 func_80033998(void)
{
    Rec80033998 *p;
    s32 i;

    p = D_8009B2FC->recs;
    for (i = 0; i < 0x28; i++) {
        if (p->unk0D == 0) {
            return 1;
        }
        p++;
    }
    return 0;
}
