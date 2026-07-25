/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern void *D_800F2AE0[];

extern void func_800738B0(void);
extern void func_800738C0(void);
extern void func_80073870(void *);

void func_80043E68(void)
{
    void **p;
    s32 n;

    p = D_800F2AE0;
    func_800738B0();
    n = 8;
    do {
        func_80073870(*p);
        p++;
    } while (--n != 0);
    func_800738C0();
}
