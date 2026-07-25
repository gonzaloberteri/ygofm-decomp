/* decomp-flags: opt=-O2 as_G=0 cc1_G=0 expand_div=1 */
#include "types.h"

extern s32 rand(void);

/* A bounded random number.  Note this is `%`, not a range scale, so the low
 * bits of the PRNG are what reach the caller. */
s32 func_800358FC(s32 n)
{
    return rand() % n;
}
