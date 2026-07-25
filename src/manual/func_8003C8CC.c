/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern u8 D_8009B37C; /* $gp + 0x474 */

extern void func_80015B00(void);
extern void func_8003C7A0(void);

u8 func_8003C8CC(void)
{
    switch (D_8009B37C & 0xF) {
    case 0:
        func_80015B00();
        break;
    case 1:
        func_8003C7A0();
        break;
    case 2:
        break;
    case 3:
        D_8009B37C = 1;
        break;
    }
    return D_8009B37C;
}
