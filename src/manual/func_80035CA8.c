/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

extern u8 D_800EAF08[0xF0];

void func_80035CA8(s32 arg0)
{
    u8 *p = D_800EAF08;
    s32 i;

    arg0++;
    for (i = 0; i < 0xF0; i++) {
        if (*p == arg0) {
            *p = 0;
        }
        p++;
    }
}
