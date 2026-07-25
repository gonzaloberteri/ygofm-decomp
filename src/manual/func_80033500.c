/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Rec80033500 {
    /* 0x0 */ u8  unk00[4];
    /* 0x4 */ s16 unk04;
    /* 0x6 */ u8  unk06[7];
    /* 0xD */ u8  unk0D;
    /* 0xE */ u8  unk0E[2];
} Rec80033500;

typedef struct Unk80033500 {
    /* 0x0000 */ Rec80033500 recs[0x2D3];
    /* 0x2D30 */ u8  unk2D30[0xC];
    /* 0x2D3C */ s16 unk2D3C;
    /* 0x2D3E */ u8  unk2D3E[0xA];
    /* 0x2D48 */ s8  unk2D48;
} Unk80033500;

s32 func_80033500(Unk80033500 *arg0)
{
    Rec80033500 *p;

    p = &arg0->recs[arg0->unk2D3C + arg0->unk2D48];
    if (p->unk0D == 0) {
        return 0;
    }
    return p->unk04;
}
