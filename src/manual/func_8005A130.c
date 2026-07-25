/* decomp-flags: opt=-O2 as_G=0 cc1_G=0 */
#include "types.h"

extern s32 func_8005F174(void);
extern s32 func_8005F18C(void);
extern u16 D_800F2B20[];

void func_8005A130(s32 arg0)
{
    s32 r;

    r = func_8005F174();
    if (r == 1) {
        if (func_8005F18C() == r) {
            return;
        }
    }
    D_800F2B20[3] = arg0;
    D_800F2B20[2] = arg0;
}
