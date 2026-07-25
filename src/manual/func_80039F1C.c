/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80039F1C {
    u8 unk00[0x33];
    u8 flags;
} Unk80039F1C;

s32 func_80039F1C(Unk80039F1C *arg0)
{
    u8 flags = arg0->flags;

    if ((flags & 0x80) == 0) {
        arg0->flags = flags | 0x80;
        return 0;
    }
    return 1;
}
