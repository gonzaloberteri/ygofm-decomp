/* decomp-flags: opt=-O1 cc1_extra=-fschedule-insns2 cc1_G=8 as_G=0 */
#include "types.h"

extern void func_80031CD4(s32, s32);

void func_80031E04(s32 arg0, s32 arg1)
{
    s32 i;

    for (i = 0; i < arg1; i++) {
        func_80031CD4(arg0, i);
    }
}
