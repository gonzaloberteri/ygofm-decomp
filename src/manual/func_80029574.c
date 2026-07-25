/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800EA0E8 {
    /* 0x00 */ s32 unk00;
    /* 0x04 */ s32 unk04;
    /* 0x08 */ u8  unk08[0x38];
} Unk800EA0E8;                                          /* size = 0x40 */

extern Unk800EA0E8 D_800EA0E8[];

void func_80029574(s32 index)
{
    Unk800EA0E8 *p = &D_800EA0E8[index];

    p->unk04 = 0;
    p->unk00 = 0;
}
