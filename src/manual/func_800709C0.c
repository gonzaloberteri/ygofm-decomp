/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"
extern s32 D_800F5B98[];
extern s32 D_800F5BE8[];
extern s32 func_8007058C(void);
extern s32 func_800705AC(void);
void func_800709C0(void) {
    s32 a; s32 b; s32 c;
    a = func_8007058C();
    b = func_8007058C();
    c = func_800705AC();
    if (D_800F5B98[a] >= D_800F5B98[b]) { c += D_800F5BE8[1]; D_800F5BE8[2] = c; } }
