/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern s32 D_8009B450;

extern void func_80073880(void *);

void func_80043D48(void **arg0)
{
    func_80073880(arg0[0]);
    func_80073880(arg0[1]);
    func_80073880(arg0[2]);
    func_80073880(arg0[3]);
    D_8009B450 = -1;
}
