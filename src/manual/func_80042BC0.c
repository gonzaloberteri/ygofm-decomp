/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80042BC0 {
    /* 0x00 */ u8  unk00[0xC];
    /* 0x0C */ u8  unk0C;
    /* 0x0D */ u8  unk0D;
    /* 0x0E */ u8  unk0E;
    /* 0x0F */ u8  unk0F[0x51];
    /* 0x60 */ s16 unk60;
} Unk80042BC0;

extern void func_8004036C(void);

void func_80042BC0(Unk80042BC0 *arg0)
{
    s32 d;

    d = arg0->unk0C - arg0->unk60;
    if (d > 0) {
        arg0->unk0E = d;
        arg0->unk0D = d;
        arg0->unk0C = d;
    } else {
        func_8004036C();
    }
}
