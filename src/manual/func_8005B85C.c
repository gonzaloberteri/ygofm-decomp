/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern void D_8005B64C(void);
extern u8 D_800117C8[];

extern void func_80014E1C(s32, u8 *, s32, s32, void (*)(void), s32, s32);

void func_8005B85C(void)
{
    func_80014E1C(1, D_800117C8, 0, 0x73, D_8005B64C, 0, 0);
}
