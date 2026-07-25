/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Unk800708C4 {
    u8 unk00[8];
    s8 unk08;
    u8 unk09[3];
} Unk800708C4;

extern Unk800708C4 D_801AB000[];
extern u8 D_800F5BE8[];

s32 func_800708C4(s32 arg0)
{
    s8 value = arg0[D_801AB000].unk08;
    s32 i;

    for (i = 0; i < 0x19; i++) {
        if (value == D_800F5BE8[i + 0x7E] - 1) {
            return 1;
        }
    }
    return 0;
}
