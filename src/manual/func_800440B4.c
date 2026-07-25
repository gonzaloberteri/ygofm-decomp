/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern u8 D_8009B437;
extern u8 D_8009B43C;
extern u8 D_8009B43D;
extern s8 D_8009B43E;
extern u8 D_8009B44F;
extern s32 D_8009B450;

s32 func_800440B4(s32 arg0, s32 arg1)
{
    if (D_8009B43E >= 0) {
        return 0;
    }
    D_8009B43C = 10;
    D_8009B437 = arg0;
    D_8009B43E = arg1;
    D_8009B44F = 0;
    D_8009B43D = 0;
    D_8009B450 = -1;
    return 1;
}
