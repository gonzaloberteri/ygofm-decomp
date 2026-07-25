/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

s32 func_80042AD8(s32 cur, s32 target, s32 step)
{
    if (target < 0) {
        cur -= step;
        if (cur < target) {
            cur = target;
        }
    } else {
        cur += step;
        if (cur > target) {
            cur = target;
        }
    }
    return cur;
}
