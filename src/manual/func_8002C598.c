/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Unk800EAD88 {
    u8  unk00[0x18];
    s16 unk18;
    u8  unk1A[2];
    u8  unk1C;
    u8  unk1D[3];
} Unk800EAD88;

extern Unk800EAD88 D_800EAD88[];
extern u8 D_8009B260;

void func_8002C598(void)
{
    s32 i;
    s32 n;

    D_8009B260 = 0;
    n = 8;
    i = 0;
    do {
        D_800EAD88[i].unk1C = 0;
        D_800EAD88[i].unk18 = -1;
        i++;
    } while (--n != 0);
}
