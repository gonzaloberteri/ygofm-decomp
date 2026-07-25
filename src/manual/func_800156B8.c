/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800E9EC8 {
    /* 0x00 */ u8 unk00[0xA];
    /* 0x0A */ s8 unk0A;
} Unk800E9EC8;

extern Unk800E9EC8 D_800E9EC8;

void func_800156B8(s32 value)
{
    u8 *base = (u8 *)&D_800E9EC8;
    s32 i;

    for (i = 0x1D; i >= 0; i--) {
        ((Unk800E9EC8 *)(base + i))->unk0A = value;
    }
}
