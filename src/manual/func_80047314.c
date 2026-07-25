/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Game80047314 {
    /* 0x0000 */ u8 unk0000[0x164B];
    /* 0x164B */ u8 unk164B;
} Game80047314;

extern Game80047314 *D_8009B45C;
extern void func_8004733C(s32, s32);

void func_80047314(u16 arg0)
{
    func_8004733C(arg0, D_8009B45C->unk164B);
}
