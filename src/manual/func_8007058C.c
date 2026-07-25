/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Reader800F5BE8 {
    /* 0x0 */ s32 unk0;
    /* 0x4 */ s32 unk4;
    /* 0x8 */ u8 *pos;
} Reader800F5BE8;

extern Reader800F5BE8 D_800F5BE8;

u8 func_8007058C(void)
{
    return *D_800F5BE8.pos++;
}
