/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk801AB000 {
    s16 unk00;
    u8  unk02[0xA];
} Unk801AB000;

extern Unk801AB000 D_801AB000[];
extern u16 D_800F5BE8[];

s32 func_80070870(s32 arg0)
{
    u16 *p;
    s16 val;
    s32 i;

    val = D_801AB000[arg0].unk00;
    i = 0;
    p = D_800F5BE8;
    for (; i < 0x20; i++) {
        if (val == p[0x1F]) {
            return 1;
        }
        p++;
    }
    return 0;
}
