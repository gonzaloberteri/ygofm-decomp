/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"
extern s32 SpuIsTransferCompleted(s32);
s16 func_800498BC(s16 arg0)
{
    if (arg0 == 0) {
        return SpuIsTransferCompleted(0);
    }
    return SpuIsTransferCompleted(1);
}
