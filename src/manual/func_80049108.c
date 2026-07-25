/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80049108 {
    u8 unk0000[0x1582];
    s16 unk1582;
    s8  unk1584;
} Unk80049108;

extern Unk80049108 *D_8009B45C;

void func_80049108(s32 arg0, s32 arg1)
{
    D_8009B45C->unk1582 = arg0;
    D_8009B45C->unk1584 = arg1;
}
