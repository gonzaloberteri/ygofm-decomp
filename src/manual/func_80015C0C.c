/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Pad800E9EC8 {
    /* 0x0 */ u8  unk0[0x6];
    /* 0x6 */ u8  unk6;
    /* 0x7 */ u8  unk7;
    /* 0x8 */ s16 unk8;
} Pad800E9EC8;

extern Pad800E9EC8 D_800E9EC8;
extern void func_80015780(void);
extern void func_8001572C(void);

void func_80015C0C(void)
{
    func_80015780();
    D_800E9EC8.unk6 |= 2;
    func_8001572C();
}
