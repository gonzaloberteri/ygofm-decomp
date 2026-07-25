/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern volatile u16 D_8009B3A4;

extern void func_80023D08(s32, s32);

void func_80023FBC(s32 arg0)
{
    s32 dir = -1;

    if (D_8009B3A4 & 0xF000) {
        if (D_8009B3A4 & 0x2000) {
            dir = 0;
        }
        if (D_8009B3A4 & 0x4000) {
            dir = 1;
        }
        if (D_8009B3A4 & 0x8000) {
            dir = 2;
        }
        if (D_8009B3A4 & 0x1000) {
            dir = 3;
        }
    }
    func_80023D08(arg0, dir);
}
