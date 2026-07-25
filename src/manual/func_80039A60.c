/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80039A60 {
    u8  unk00[0x34];
    u16 unk34;
} Unk80039A60;

void func_800393B0(Unk80039A60 *arg0);

void func_80039A60(Unk80039A60 *arg0)
{
    arg0->unk34 |= 0xA00;
    do {
        func_800393B0(arg0);
    } while (!(arg0->unk34 & 0x2000));
}
