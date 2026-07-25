/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Pad800E9EC8 {
    /* 0x0 */ u8  unk0[0x4];
    /* 0x4 */ u8  unk4;
    /* 0x5 */ u8  unk5;
    /* 0x6 */ u8  unk6;
    /* 0x7 */ u8  unk7;
    /* 0x8 */ s16 unk8;
} Pad800E9EC8;

extern Pad800E9EC8 D_800E9EC8;
extern void func_800156B8(s32);
extern void func_80015870(void);

void func_800158B8(void)
{
    D_800E9EC8.unk8 = 0xFF;
    D_800E9EC8.unk5 = 0;
    D_800E9EC8.unk6 = 0x80;
    func_800156B8(D_800E9EC8.unk4);
    D_800E9EC8.unk7 = 0xC;
    func_80015870();
}
