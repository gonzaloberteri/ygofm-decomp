/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800F0548 {
    /* 0x00 */ u8  unk00[8];
    /* 0x08 */ u16 flags;
    /* 0x0A */ u8  unk0A[0x66];
} Unk800F0548;                                          /* size = 0x70 */

extern Unk800F0548 D_800F0548[];

s32 func_8004002C(void)
{
    Unk800F0548 *p = D_800F0548;
    s32 i;

    for (i = 0x10; i < 0x60; i++) {
        if ((p->flags & 0x80) == 0) {
            return i;
        }
        p++;
    }
    return -1;
}
