/* decomp-flags: opt=-O1 as_G=0 cc1_G=0 */
#include "types.h"

typedef struct Unk800EB184 {
    u8  unk00[0xC];
    u8  unk0C;
    u8  unk0D;
    u8  unk0E;
} Unk800EB184;

extern Unk800EB184 *D_800EB184;

void func_80030090(void)
{
    Unk800EB184 *p = D_800EB184;

    p->unk0E = 0x40;
    p->unk0D = 0x40;
    p->unk0C = 0x40;
}
