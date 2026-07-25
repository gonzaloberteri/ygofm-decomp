/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern u16 D_801D0200[];

s32 func_8002C4DC(s32 key)
{
    u16 *p = D_801D0200;
    s32 i;

    for (i = 0; i < 0x28; i++) {
        if (*p == key) {
            return i;
        }
        p++;
    }
    return -1;
}
