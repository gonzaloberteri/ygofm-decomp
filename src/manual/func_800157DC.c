/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800E9EC8 {
    u8 unk00[6];
    u8 unk06;
    u8 unk07;
    u8 unk08[8];
} Unk800E9EC8;

extern Unk800E9EC8 D_800E9EC8;

void func_80015780(void);
void func_8001572C(void);

void func_800157DC(void)
{
    func_80015780();
    D_800E9EC8.unk07 = 8;
    D_800E9EC8.unk06 |= 1;
    func_8001572C();
}
