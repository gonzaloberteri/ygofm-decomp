/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Actor800429D8 {
    /* 0x00 */ u8  unk00[0x36];
    /* 0x36 */ s16 unk36;
    /* 0x38 */ s16 unk38;
    /* 0x3A */ s16 unk3A;
    /* 0x3C */ u8  unk3C[0x26];
    /* 0x62 */ u8  unk62;
    /* 0x63 */ u8  unk63;
    /* 0x64 */ u8  unk64;
} Actor800429D8;

void func_800429D8(Actor800429D8 *actor)
{
    if (actor != NULL) {
        actor->unk36 = 0;
        actor->unk38 = 0;
        actor->unk3A = 0;
        actor->unk62 = 0x80;
        actor->unk63 = 0x80;
        actor->unk64 = 0x80;
    }
}
