/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Unk800E9EC8 {
    s32 unk00;
    u8  unk04;
    u8  unk05;
    u8  unk06;
    u8  unk07[0x9];
} Unk800E9EC8;

extern Unk800E9EC8 D_800E9EC8;
extern u8 D_8009B145;

extern void func_80015780(void);
extern void func_8001572C(void);

void func_8001581C(s32 arg0)
{
    if (arg0 == 0xFFFFFF) {
        D_8009B145 = 1;
    }
    D_800E9EC8.unk00 = arg0;
    func_80015780();
    D_800E9EC8.unk06 |= 0x30;
    func_8001572C();
}
