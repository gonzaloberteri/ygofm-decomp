/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Pad800E9EC8 {
    /* 0x0 */ u8  unk0[0x6];
    /* 0x6 */ u8  unk6;
    /* 0x7 */ u8  unk7;
    /* 0x8 */ s16 unk8;
} Pad800E9EC8;

extern Pad800E9EC8 D_800E9EC8;
extern void func_800158B8(void);
extern void func_80015870(void);

void func_80015CC0(void)
{
    func_800158B8();
    D_800E9EC8.unk6 |= 6;
    func_80015870();
}
