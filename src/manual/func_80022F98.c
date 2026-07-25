/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

typedef struct Ent {
    /* 0x00 */ u8   unk00[0x24];
    /* 0x24 */ void *unk24;
    /* 0x28 */ s16  unk28;
    /* 0x2A */ s16  unk2A;
    /* 0x2C */ s16  unk2C;
    /* 0x2E */ u8   unk2E[0x2];
    /* 0x30 */ u16  unk30;
    /* 0x32 */ u16  unk32;
    /* 0x34 */ u8   unk34[0x38];
    /* 0x6C */ u8   unk6C;
} Ent;

typedef struct Unk80022F98 {
    /* 0x00 */ Ent *unk00;
    /* 0x04 */ u8  unk04[0x13];
    /* 0x17 */ u8  unk17;
} Unk80022F98;

extern void func_80022EEC(void);

void func_80022F98(Unk80022F98 *arg0, Ent *arg1)
{
    Ent *b;
    s32 t;

    if (arg1 != NULL) {
        b = arg0->unk00;
        arg1->unk28 = arg1->unk30 - b->unk30;
        arg1->unk2A = arg1->unk32 - b->unk32;
        t = arg0->unk17;
        arg1->unk6C = 1;
        arg1->unk24 = func_80022EEC;
        arg1->unk2C = t;
    }
}
