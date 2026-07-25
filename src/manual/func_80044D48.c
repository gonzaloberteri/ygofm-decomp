/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Game80044D48 {
    /* 0x0000 */ u8  unk0000[0x512];
    /* 0x0512 */ s16 unk0512;
    /* 0x0514 */ u8  unk0514[0x28];
    /* 0x053C */ u8  unk053C[0x200];
    /* 0x073C */ u8  unk073C[0x200];
    /* 0x093C */ u8  unk093C[0x200];
    /* 0x0B3C */ u8  unk0B3C[0xA00];
    /* 0x153C */ u8 *unk153C;
    /* 0x1540 */ u8 *unk1540;
    /* 0x1544 */ u8 *unk1544;
    /* 0x1548 */ u8 *unk1548;
} Game80044D48;

extern Game80044D48 *D_8009B45C;
extern void func_80044DA0(void);
extern void func_80044DC0(s32);

void func_80044D48(void)
{
    Game80044D48 *g;
    u8 *t;

    func_80044DA0();
    func_80044DC0(0xFF);
    g = D_8009B45C;
    g->unk153C = g->unk053C;
    g->unk1540 = g->unk073C;
    g->unk1544 = g->unk093C;
    t = g->unk0B3C;
    g->unk0512 = 0;
    g->unk1548 = t;
}
