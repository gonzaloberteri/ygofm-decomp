/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"
typedef struct Big800E9E90 { s32 unk_0; s32 unk_4; s32 unk_8; } Big800E9E90;
extern Big800E9E90 D_800E9E90;
extern s32 D_8009B0F4;
extern s32 func_8007E710(s32);
void func_80014390(u8 arg0, s32 arg1)
{
    s32 v;
    if (arg0 != 2) {
        return;
    }
    v = func_8007E710(arg1);
    if (v > 0) {
        D_800E9E90.unk_0 = v;
    }
    D_8009B0F4 &= ~0x800;
}
