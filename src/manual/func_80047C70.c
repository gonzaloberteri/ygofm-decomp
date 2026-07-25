/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern void SpuSetKey(s32, u32);
extern s32 SpuGetKeyStatus(u32);

void func_80047C70(u32 arg0)
{
    s32 i;

    i = 0;
    do {
        SpuSetKey(0, arg0);
        if (SpuGetKeyStatus(arg0) == 0) {
            break;
        }
        i++;
    } while (i < 0x100);
}
