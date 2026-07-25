/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Sound {
    /* 0x00 */ s8 unk_00[6];
    /* 0x06 */ u8 unk_06;
    /* 0x07 */ u8 unk_07;
} Sound;

extern Sound D_800E9EC8;

extern void func_800158B8(void);
extern void func_80015870(void);

void func_80015904(void)
{
    Sound *snd = &D_800E9EC8;

    func_800158B8();
    snd->unk_07 = 8;
    snd->unk_06 |= 1;
    func_80015870();
}
