/* decomp-flags: opt=-O2 as_G=0 cc1_G=0 */
#include "types.h"

extern char D_80011908[];
extern char D_80011918[];
extern s32 func_8007058C(void);
extern void printf(const char *, ...);

void func_800736C4(void)
{
    s32 v;

    v = func_8007058C();
    printf(D_80011908);
    printf(D_80011918, v);
}
