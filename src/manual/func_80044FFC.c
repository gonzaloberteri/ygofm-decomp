/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Msg80044FFC {
    /* 0x00 */ u8  unk00;
    /* 0x01 */ u8  unk01;
    /* 0x02 */ u16 unk02;
    /* 0x04 */ u8  unk04[4];
    /* 0x08 */ s32 unk08;
    /* 0x0C */ u8  unk0C[0x24];
} Msg80044FFC;

extern void func_80045BE8(Msg80044FFC *);

void func_80044FFC(s32 arg0, s32 arg1, s32 arg2)
{
    Msg80044FFC msg;

    msg.unk00 = 0x29;
    msg.unk08 = (s16)arg0;
    msg.unk02 = (u8)arg1;
    msg.unk01 = arg2;
    func_80045BE8(&msg);
}
