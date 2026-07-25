/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct GameState {
    /* 0x0000 */ s8 unk_0000[0x1582];
    /* 0x1582 */ s16 unk_1582;
    /* 0x1584 */ s8 unk_1584;
} GameState;

extern GameState *D_8009B45C;

void func_800490F0(s16 arg0, s8 arg1)
{
    D_8009B45C->unk_1582 = arg0;
    D_8009B45C->unk_1584 = arg1;
}
