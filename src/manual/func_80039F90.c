/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

void func_8004036C(s32 arg0);

void func_80039F90(s32 *arg0)
{
    s32 i;

    for (i = 2; i >= 0; i--) {
        func_8004036C(arg0[i]);
        arg0[i] = 0;
    }
}
