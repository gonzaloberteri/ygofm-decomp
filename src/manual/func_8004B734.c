/* decomp-flags: opt=-O2 as_G=0 cc1_G=8 cc1_extra=-fno-strength-reduce */
#include "game.h"

/* D_8009B458 is named at every use rather than bound to a local: the loop calls
 * out, a call may clobber a global, so naming it forces the `lui %hi / lw %lo`
 * reload the original has on every iteration.  See PLAN.md, 2026-07-25. */

extern s32  GetRCnt(u32);
extern void func_8004C8C8(void);
extern void func_8004C84C(void);
extern void func_8004AAFC(void);

s32 func_8004B734(void)
{
    s32 i;

    if (D_8009B458->unk_814 == 0) {
        return 1;
    }
    if (D_8009B458->unk_500 != 0) {
        return 1;
    }
    if (D_8009B458->unk_509 != 0) {
        return 1;
    }
    if (D_8009B458->unk_501 == 0) {
        GetRCnt(0xF2000002);

        D_8009B458->unk_501 = 1;
        for (i = 0; i < 8; i++) {
            func_8004C8C8();
            D_8009B458->unk_508++;
            if (D_8009B458->unk_508 >= 0xB) {
                D_8009B458->unk_508 = 0;
                func_8004C84C();
                func_8004AAFC();
                if (D_8009B458->unk_50C != NULL) {
                    D_8009B458->unk_50C();
                }
            }
        }
        D_8009B458->unk_501 = 0;
    }
    return 0;
}
