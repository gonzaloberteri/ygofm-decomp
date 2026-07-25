/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80042A28 {
    u8  unk00[0x32];
    s16 unk32;
    u8  unk34[0x4];
    s16 unk38;
    u8  unk3A[0x29];
    u8  unk63;
} Unk80042A28;

void func_80042A28(Unk80042A28 *arg0)
{
    s32 acc;

    acc = ((arg0->unk32 << 8) | arg0->unk63) + arg0->unk38;
    arg0->unk63 = acc;
    arg0->unk32 = acc >> 8;
}
