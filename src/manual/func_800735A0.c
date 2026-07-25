/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

extern s32 D_800F5B98[];
extern s32 func_800705AC(void);
extern s32 func_8007058C(void);

void func_800735A0(void)
{
    s32 v = func_800705AC();

    D_800F5B98[func_8007058C()] = v;
}
