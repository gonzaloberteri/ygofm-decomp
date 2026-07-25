/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Unk800F2C40 {
    u8 unk0000[0xE14];
    u8 unkE14;
    u8 unkE15[0xA];
    u8 unkE1F;
    u8 unkE20[0xE20 - 0xE20];
} Unk800F2C40;

extern Unk800F2C40 D_800F2C40[];

s32 func_80058DD8(s32 index)
{
    Unk800F2C40 *p = &D_800F2C40[index];

    if (p->unkE14 != 0xFF) {
        return 2;
    }
    return p->unkE1F != 0;
}
