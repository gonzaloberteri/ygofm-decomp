/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct GameState {
    /* 0x0000 */ s8 unk_0000[0x510];
    /* 0x0510 */ u16 unk_0510;
} GameState;

extern GameState *D_8009B458;

s32 func_80049600(s32 arg0)
{
    u8 value = arg0;

    if (value >= 0x15) {
        return 0xFF;
    }
    if (value == 0) {
        return 0xFF;
    }
    D_8009B458->unk_0510 = (u8)arg0;
    return value;
}
