/* decomp-flags: opt=-O1 cc1_extra=-fschedule-insns2 cc1_G=8 as_G=0 */
#include "types.h"

typedef struct Unk800599FC {
    s32 unk00;
    s32 unk04;
    s32 unk08;
    s32 unk0C;
    s32 unk10;
    s32 unk14;
    s32 unk18;
    s32 unk1C;
} Unk800599FC;

extern void func_80058B4C(Unk800599FC *, s32, s32, s32, s32, s32, s32, s32);

void func_800599FC(s32 arg0, s32 arg1, s32 arg2, s32 arg3, s32 arg4, s32 arg5,
                   s32 arg6)
{
    Unk800599FC sp20;

    func_80058B4C(&sp20, arg0, arg1, arg2, arg3, arg4, arg5, arg6);
}
