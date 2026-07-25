/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

extern s32 D_800F5B98[];
extern s32 func_8007058C(void);

void func_80070EB4(void)
{
    s32 a;
    s32 b;
    s32 c;

    a = func_8007058C();
    b = func_8007058C();
    c = func_8007058C();
    D_800F5B98[c] = D_800F5B98[a] - D_800F5B98[b];
}
