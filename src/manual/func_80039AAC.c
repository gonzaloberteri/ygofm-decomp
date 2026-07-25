/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Actor {
    /* 0x00 */ s8 unk_00[0x13];
    /* 0x13 */ u8 flags;
} Actor;

/* Sets bit 7 of the flag byte, returning 1 if it was already set. */
s32 func_80039AAC(Actor *actor)
{
    u8 flags = actor->flags;

    if (!(flags & 0x80)) {
        actor->flags = flags | 0x80;
        return 0;
    }
    return 1;
}
