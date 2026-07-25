/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern u8 D_8009B3C6;
extern volatile u16 D_8009B3FA;

void func_8003E46C(u8 arg0, u32 arg1)
{
    u32 tmp;

    arg1 |= 0x80;
    D_8009B3C6 = arg0;
    tmp = D_8009B3FA & 0xFF87;
    D_8009B3FA = tmp;
    D_8009B3FA = tmp | arg1;
}
