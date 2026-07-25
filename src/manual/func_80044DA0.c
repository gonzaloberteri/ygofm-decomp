/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct GameState {
    /* 0x0000 */ s8 unk_0000[0x514];
    /* 0x0514 */ u8 unk_0514;
    /* 0x0515 */ u8 unk_0515;
} GameState;

extern GameState *D_8009B45C;

void func_80044DA0(void)
{
    D_8009B45C->unk_0514 = 0x80;
    D_8009B45C->unk_0515 = 0x80;
}
