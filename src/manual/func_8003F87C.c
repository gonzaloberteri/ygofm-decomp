/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern u8 D_801D3200[];
extern u8 D_801D0200[];
extern u8 D_80010384[];

extern void func_800356A0(u8 *, u8 *, s32);
extern void func_8003D03C(u8 *);
extern void func_8003F758(u8 *, s32, u8 *, s32);

void func_8003F87C(void)
{
    u8 *buf = D_801D3200;

    func_800356A0(buf, D_801D0200, 0x680);
    func_8003D03C(buf - 0x200);
    func_8003F758(buf, 0xD00, D_80010384, 2);
}
