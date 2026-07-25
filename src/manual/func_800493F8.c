/* decomp-flags: opt=-O2 as_G=0 cc1_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"

typedef struct Unk800493F8 {
    /* 0x0000 */ u8  unk0000[0x1564];
    /* 0x1564 */ u16 *unk1564;
} Unk800493F8;

extern Unk800493F8 *D_8009B45C;
extern void func_80049010(void);

void func_800493F8(void)
{
    u16 *p;

    func_80049010();
    p = (u16 *)0x801EA800;
    D_8009B45C->unk1564 = p;
    *p = 0xFFFF;
}
