/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Unk800591C0 {
    u8 unk00[0x10];
} Unk800591C0;

extern Unk800591C0 D_800F39B0[][226];

Unk800591C0 *func_800591C0(s32 arg0, u32 arg1)
{
    Unk800591C0 *row;

    if (arg1 >= 3) {
        arg1 = 0;
    }
    row = D_800F39B0[arg0];
    return &row[arg1];
}
