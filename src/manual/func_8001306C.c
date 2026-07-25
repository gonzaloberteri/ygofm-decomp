/* decomp-flags: opt=-O2 as_G=8 cc1_extra=-fno-strength-reduce */
#include "types.h"

/* The per-frame tick: run the four registered callbacks in D_800E9DB0, then
 * the one in D_8009B0B8, then resync the frame pacing. */

typedef void (*Callback)(void);

extern Callback D_800E9DB0[4];
extern Callback D_8009B0B8;      /* gp + 0x1B0 */
extern s32      D_8009AF08;      /* gp + 0x000 */
extern s32      D_8009B0A4;      /* gp + 0x19C */
extern s32      D_8009B0B0;      /* gp + 0x1A8 */
extern s32      D_8009B0BC;      /* gp + 0x1B4 */
extern s32      D_8009B0D4;      /* gp + 0x1CC */

extern void func_800154E4(void);
extern void func_80041340(void);
extern void func_80014A5C(s32);
extern void func_800136D4(void);

void func_8001306C(void)
{
    s32 i;
    Callback *p;

    func_800154E4();
    func_80041340();

    /* `i` is initialised before `p`: that order is what puts the counter in
     * $s1 and the cursor in $s0, the way the original allocates them. */
    i = 0;
    p = D_800E9DB0;
    for (; i < 4; i++) {
        if (*p != NULL) {
            (*p)();
        }
        p++;
    }

    if (D_8009B0B8 != NULL) {
        D_8009B0B8();
    }

    if (D_8009B0B0 < D_8009B0A4 || D_8009B0BC < D_8009B0D4 || --D_8009AF08 < 0) {
        D_8009AF08 = 0x3C;
        D_8009B0B0 = D_8009B0A4;
        D_8009B0BC = D_8009B0D4;
    }

    func_80014A5C(0);
    func_800136D4();
}
