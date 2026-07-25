/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8009B458 {
    s8 unk00;
    s8 unk01[0x17];
} Unk8009B458;

extern Unk8009B458 *D_8009B458;

void func_8004B6E8(u8 index, s8 value)
{
    Unk8009B458 *p;

    p = D_8009B458;
    p += index;
    p->unk00 = value;
}
