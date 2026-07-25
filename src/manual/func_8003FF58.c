/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern void func_80047430(s16, s32);

void func_8003FF58(s32 arg0)
{
    if (arg0 > 0) {
        arg0 = -arg0;
    }
    func_80047430(arg0, 0);
}
