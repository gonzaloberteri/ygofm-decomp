/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern u8 D_801D3200[];
extern u8 D_80010384[];
extern u8 D_8009B0D1;

extern void func_8003F758(u8 *, s32, u8 *, s32);

void func_8003F7D4(void)
{
    D_8009B0D1 = 0;
    func_8003F758(D_801D3200, 0x680, D_80010384, 0);
}
