/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"
extern s32 func_8002CCA8(s32);
extern void func_8003BF00(void);
extern void func_80014E1C(f32, f32, s32, s32, void *, s32, s32);
extern void func_800137E4(void);
void func_8003C0C0(void)
{
    s32 x = 0;

    if (func_8002CCA8(0x47) != 0) {
        x = 0x9E;
    }
    func_80014E1C(0.0f, 0.0f, x + 0x1FD9, 0x9E, func_8003BF00, 0, 0);
    func_800137E4();
}
