/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern s32 D_800E9DB0[4];
extern s32 D_8009B0B8;

void func_800134B4(void)
{
    s32 i;

    for (i = 3; i >= 0; i--) {
        D_800E9DB0[i] = 0;
    }
    D_8009B0B8 = 0;
}
