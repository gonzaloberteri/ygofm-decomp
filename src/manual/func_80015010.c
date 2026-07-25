/* decomp-flags: opt=-O1 as_G=8 */
#include "types.h"

extern volatile u16 D_8009B112;

void func_80015010(void)
{
    D_8009B112 &= 0x3FFC;
    D_8009B112 |= 2;
}
