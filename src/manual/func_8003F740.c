/* decomp-flags: opt=-O3 as_G=8 */
#include "types.h"

/* $gp = 0x8009AF08 */
extern u16 D_8009B3FA;  /* gp + 0x4F2 */
extern u8  D_8009B3DE;  /* gp + 0x4D6 */
extern u8  D_8009B3C1;  /* gp + 0x4B9 */

void func_8003F740(u8 arg0)
{
    D_8009B3FA = 0x8000;
    D_8009B3DE = arg0;
    D_8009B3C1 = 0;
}
