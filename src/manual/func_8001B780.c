/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Unk8001B780Sub {
    u8  unk00[0x30];
    s16 unk30;
    s16 unk32;
} Unk8001B780Sub;

typedef struct Unk8001B780 {
    u8               unk00[0x4];
    Unk8001B780Sub  *unk04;
    u8               unk08[0x6];
    s8               unk0E;
} Unk8001B780;

void func_8001B780(Unk8001B780 *arg0)
{
    s32 x;
    Unk8001B780Sub *sub;

    x = arg0->unk0E * 60;
    sub = arg0->unk04;
    sub->unk30 = x + 0xE;
    sub->unk32 = 0xC2;
}
