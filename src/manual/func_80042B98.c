/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

s32 func_80042B98(u8 *arg0)
{
    u8 v = arg0[0x6C];

    if (!(v & 0x80)) {
        arg0[0x6C] = v | 0x80;
        return 0;
    }
    return 1;
}
