/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern u8 D_8009AF98;
extern s8 D_8009AF99;
extern s32 func_8005F174(void);
extern s32 func_8005F18C(void);

void func_8005A188(s32 arg0)
{
    if (func_8005F174() == 1 && func_8005F18C() == 1) {
        return;
    }
    if (arg0 >= 0) {
        D_8009AF99 = 1;
    } else {
        D_8009AF99 = -1;
    }
    D_8009AF98 = 0xFF;
}
