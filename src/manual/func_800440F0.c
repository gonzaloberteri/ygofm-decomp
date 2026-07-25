/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern u8 D_800F2AE0[];
extern s32 func_800440B4(s32, s32);
extern void func_80043D48(u8 *);
extern void func_8008B330(s32);

s32 func_800440F0(s32 arg0)
{
    if (func_800440B4(arg0, 1) == 0) {
        return 0;
    }
    func_80043D48(D_800F2AE0);
    func_8008B330(arg0);
    return 1;
}
