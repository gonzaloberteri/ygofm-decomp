/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

extern s32 D_800F5BE8[];
extern s32 func_800705AC(void);

void func_80070988(void)
{
    D_800F5BE8[2] = func_800705AC() + D_800F5BE8[1];
}
