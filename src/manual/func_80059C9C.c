/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern void func_800533D8(void);
extern void func_800530C4(void);

extern s8 D_8009AF94;
extern s8 D_8009AF9A;

void func_80059C9C(void)
{
    s8 value;

    func_800533D8();
    func_800530C4();
    value = 0x14;
    D_8009AF94 = value;
    value = -1;
    D_8009AF9A = value;
}
