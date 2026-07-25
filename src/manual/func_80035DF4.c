/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"
typedef struct S { u8 unk00[0x11]; u8 unk11; u8 unk12[6]; u8 unk18; u8 unk19[3]; } S;
extern S D_800EB288[];
void func_80035DF4(void) {
    s32 i;
    s32 n;
    n = 620;
    i = 0;
    do {
        D_800EB288[i].unk11 = 0;
        D_800EB288[i].unk18 = 0;
        i++;
    } while (--n != 0);
}
