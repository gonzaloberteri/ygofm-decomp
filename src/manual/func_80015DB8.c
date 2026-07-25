/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Rec70 {
    /* 0x00 */ u8  unk_00[0x28];
    /* 0x28 */ s32 unk_28;
    /* 0x2C */ u8  unk_2C[0x70 - 0x2C];
} Rec70;

typedef struct Ent {
    /* 0x00 */ u8  unk_00[0x28];
    /* 0x28 */ s32 unk_28;
    /* 0x2C */ u8  unk_2C[0x6A - 0x2C];
    /* 0x6A */ u8  unk_6A;
} Ent;

extern Rec70 D_800EFE48[];
extern void func_80015D18(Ent *);

void func_80015DB8(Ent *e)
{
    s32 off = e->unk_6A * 0x70;

    e->unk_28 = ((Rec70 *)(off + (u8 *)D_800EFE48))->unk_28;
    func_80015D18(e);
}
