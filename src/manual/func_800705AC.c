/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns2 */
#include "types.h"
typedef struct Reader800F5BE8 { s32 unk0; s32 unk4; u8 *pos; } Reader800F5BE8;
extern Reader800F5BE8 D_800F5BE8;
s32 func_800705AC(void)
{
    u8 *p;
    p = D_800F5BE8.pos;
    D_800F5BE8.pos = p + 2;
    return p[0] | (p[1] << 8);
}
