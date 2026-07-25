/* decomp-flags: opt=-O2 as_G=8 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

typedef struct Unk80025EE0 {
    /* 0x00 */ s16 unk00;
    /* 0x02 */ s16 unk02;
    /* 0x04 */ u8  unk04[0x16];
    /* 0x1A */ s16 unk1A;
} Unk80025EE0;

extern s32 func_80024E24(void);
extern Unk80025EE0 *func_8002C68C(s32);
extern void func_8003FEE0(s32);
extern u16 D_8009B220;

void func_80025EE0(void)
{
    Unk80025EE0 *p;

    if (func_80024E24() == 0) {
        p = func_8002C68C(0x12);
        p->unk00 = 0xA0;
        p->unk02 = 0x78;
        p->unk1A = 1;
        func_8003FEE0(2);
    } else {
        D_8009B220 = 0;
    }
}
