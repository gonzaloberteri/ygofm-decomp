/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800EB0F8 {
    u8  unk00[0x28];
    u32 unk28;
    u32 unk2C;
    u32 unk30;
    u16 unk34;
    u8  unk36[0x2E];
} Unk800EB0F8;

extern Unk800EB0F8 D_800EB0F8[];

extern void func_80035CE4(void);
extern void func_80035DF4(void);

void func_80035A64(void)
{
    s32 i;
    s32 n;

    n = 4;
    i = 0;
    do {
        D_800EB0F8[i].unk34 = 0;
        D_800EB0F8[i].unk30 = 0;
        D_800EB0F8[i].unk2C = 0;
        D_800EB0F8[i].unk28 = 0;
        i++;
    } while (--n != 0);
    func_80035CE4();
    func_80035DF4();
}
