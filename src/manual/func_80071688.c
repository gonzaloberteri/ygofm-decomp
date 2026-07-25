/* decomp-flags: opt=-O2 cc1_extra=-fno-schedule-insns2 cc1_G=0 as_G=0 */
#include "types.h"
extern s32 D_800F5B98[];
extern u8 D_800F5C82;
extern s32 func_8007058C(void);
void func_80071688(void)
{
    func_8007058C()[D_800F5B98] = D_800F5C82;
}
