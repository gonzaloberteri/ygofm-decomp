/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern void func_8003BA14(void);
extern void func_80014E1C(f32, f32, s32, s32, void *, s32, s32);
extern void func_800137E4(void);

void func_8003BBF8(void)
{
    func_80014E1C(0.0f, 0.0f, 0x1EDF, 0x50, func_8003BA14, 0, 0);
    func_800137E4();
}
