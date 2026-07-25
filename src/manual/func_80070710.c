/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800917F0 {
    /* 0x00 */ s8 unk00;
    /* 0x01 */ u8 unk01[8];
} Unk800917F0;                                          /* size = 9 */

extern Unk800917F0 D_800917F0[];
extern s8 D_8009B361;

s32 func_80070710(void)
{
    return D_800917F0[D_8009B361].unk00;
}
