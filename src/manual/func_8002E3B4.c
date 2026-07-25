/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern u16 D_8009B27C;

s32 func_8002E3B4(void)
{
    u16 v;

    v = D_8009B27C;
    if (!(v & 0x8000)) {
        D_8009B27C = v | 0x8000;
        return 0;
    }
    return 1;
}
