/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80042A50 {
    u8  unk00[0x34];
    s16 unk34;
    u8  unk36[0x4];
    s16 unk3A;
    u8  unk3C[0x28];
    u8  unk64;
} Unk80042A50;

void func_80042A50(Unk80042A50 *arg0)
{
    s32 temp;

    temp = ((arg0->unk34 << 8) | arg0->unk64) + arg0->unk3A;
    arg0->unk64 = temp;
    arg0->unk34 = temp >> 8;
}
