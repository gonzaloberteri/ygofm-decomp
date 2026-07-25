/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

typedef struct Unk800E9EC8 {
    /* 0x00 */ u8 unk00[4];
    /* 0x04 */ s8 unk04;
    /* 0x05 */ s8 unk05;
    /* 0x06 */ s8 unk06;
    /* 0x07 */ s8 unk07;
    /* 0x08 */ u8 unk08[0x20];
} Unk800E9EC8;

extern Unk800E9EC8 D_800E9EC8;
extern s8 D_8009B145;

void func_800151B0(void)
{
    D_800E9EC8.unk06 = 0;
    D_800E9EC8.unk04 = 0;
    D_800E9EC8.unk05 = 0;
    D_800E9EC8.unk07 = 8;
    D_8009B145 = 0;
}
