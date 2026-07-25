/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern volatile u32 D_8009B0F4;

extern void func_80015010(void);

void func_80015038(void)
{
    if (D_8009B0F4 & 0x10) {
        if (D_8009B0F4 & 0x80000) {
            func_80015010();
        }
    }
}
