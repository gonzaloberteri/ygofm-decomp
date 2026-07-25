/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80039A14 {
    u8  unk00[0x34];
    u16 unk34;
} Unk80039A14;

extern void func_800393B0(Unk80039A14 *);

void func_80039A14(Unk80039A14 *arg0)
{
    arg0->unk34 |= 0x800;
    do {
        func_800393B0(arg0);
    } while (!(arg0->unk34 & 0x2000));
}
