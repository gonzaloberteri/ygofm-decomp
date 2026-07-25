/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

extern s32 D_800F5B98[];
extern u8 D_8009B364;
extern s32 func_8007058C(void);

void func_80071460(void)
{
    D_800F5B98[func_8007058C()] = D_8009B364;
}
