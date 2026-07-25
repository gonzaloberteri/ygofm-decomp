/* decomp-flags: opt=-O2 as_G=0 cc1_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"
extern s32 D_800F5B98[];
extern u16 D_800F5C80;
extern s32 func_8007058C(void);
void func_8007164C(void)
{
    D_800F5B98[func_8007058C()] = D_800F5C80;
}
