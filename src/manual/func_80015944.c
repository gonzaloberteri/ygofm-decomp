/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Unk800E9EC8 {
    s32 unk00;
    u8  unk04;
    u8  unk05;
    u8  unk06;
    u8  unk07;
    u8  unk08[8];
} Unk800E9EC8;

extern Unk800E9EC8 D_800E9EC8;
extern u8 D_8009B145;   /* gp + 0x23D */

void func_800158B8(void);
void func_80015870(void);

void func_80015944(s32 arg0)
{
    if (arg0 == 0xFFFFFF) {
        D_8009B145 = 1;
    }
    D_800E9EC8.unk00 = arg0;
    func_800158B8();
    D_800E9EC8.unk06 |= 0x30;
    func_80015870();
}
