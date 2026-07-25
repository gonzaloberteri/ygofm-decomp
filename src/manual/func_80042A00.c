/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Actor {
    /* 0x00 */ u8  unk00[0x30];
    /* 0x30 */ s16 x;
    /* 0x32 */ u8  unk32[0x4];
    /* 0x36 */ s16 velX;
    /* 0x38 */ u8  unk38[0x2A];
    /* 0x62 */ u8  xFrac;
} Actor;

void func_80042A00(Actor *actor)
{
    s32 pos;

    pos = (actor->x << 8) | actor->xFrac;
    pos += actor->velX;
    actor->xFrac = pos;
    actor->x = pos >> 8;
}
