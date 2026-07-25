/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk801D0000 {
    /* 0x000 */ u8 unk000[0x618];
    /* 0x618 */ u8 unk618[0x100];
} Unk801D0000;

extern Unk801D0000 D_801D0000;

s32 func_8002CCA8(s32 arg0)
{
    s32 v;

    v = D_801D0000.unk618[(arg0 & 0x7FF) >> 3] & (0x80 >> (arg0 & 7));
    if (arg0 & 0x8000) {
        v = (v == 0);
    }
    return v;
}
