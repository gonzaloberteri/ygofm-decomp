/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern s32 D_800F5918[];

void func_80060170(s32 arg0, s32 arg1)
{
    s32 *a = D_800F5918;
    s32 i = 0;
    s32 *b = a + 1;

    do {
        if (*b == arg0) {
            return;
        }
        if (*b == 0 && *a == 0) {
            *b = arg0;
            *a = arg1;
            return;
        }
        i++;
        b += 2;
        a += 2;
    } while (i < 0x50);
}
