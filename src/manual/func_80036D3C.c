/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"
typedef struct Unk80036D3C { u8 *unk00[0x16]; s8 unk58; } Unk80036D3C;
s32 func_80036D3C(Unk80036D3C *arg0) {
    u8 **slot;
    u8 *p;
    slot = &arg0->unk00[arg0->unk58];
    p = *slot;
    *slot = p + 2;
    return p[0] | (p[1] << 8);
}
