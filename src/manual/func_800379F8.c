/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Unk800379F8 {
    /* 0x00 */ u8 unk00[0x51];
    /* 0x51 */ u8 unk51;
} Unk800379F8;

extern u16 D_8009B322;
extern s32 func_80036D3C(void);

void func_800379F8(Unk800379F8 *arg0)
{
    s32 v;

    if ((arg0->unk51 & 0x80) == 0) {
        arg0->unk51 |= 0x80;
        D_8009B322 = func_80036D3C();
    }
    v = D_8009B322 - 1;
    D_8009B322 = v;
    if ((s16)v == 0) {
        arg0->unk51 = 0;
    }
}
