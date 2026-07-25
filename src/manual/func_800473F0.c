/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

void func_80045114(void);
void func_80049230(s32 arg0, s16 arg1);

void func_800473F0(s32 arg0, s32 arg1)
{
    if ((arg0 & 0x8000) != 0) {
        func_80045114();
    } else {
        func_80049230(-1, arg1);
    }
}
