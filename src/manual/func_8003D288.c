/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8003D288 {
    /* 0x000 */ u8  unk000[0x334];
    /* 0x334 */ s32 unk334;
} Unk8003D288;

s32 func_8003D288(Unk8003D288 *a, Unk8003D288 *b)
{
    s32 i;

    if (a->unk334 == b->unk334) {
        for (i = 5; i >= 0; i--) {
        }
        return 1;
    }
    return 0;
}
