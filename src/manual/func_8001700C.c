/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8001700C {
    /* 0x00 */ u8  unk00[0x16];
    /* 0x16 */ u16 unk16;
} Unk8001700C;

s32 func_8001700C(Unk8001700C *arg0)
{
    u16 flags;

    flags = arg0->unk16;
    if (flags & 0x8000) {
        if (!(flags & 0x4000)) {
            return 1;
        }
    }
    return 0;
}
