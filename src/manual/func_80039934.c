/* decomp-flags: opt=-Os as_G=0 */
#include "types.h"

/* Moves a widget and its three attached sprites.  Two of the sprites hand off
 * to a helper when their type is 4 instead of being positioned directly.
 *
 * Two locals, not one and not three: the first two sprites share `spr` and the
 * third has its own.  That is what puts all three pointers in $a0 -- with one
 * local they all land in $a3, with three the first lands in $v0. */

typedef struct Spr80039934 {
    /* 0x00 */ char pad_00[0x1E];
    /* 0x1E */ s16  unk_1E;
    /* 0x20 */ char pad_20[0x10];
    /* 0x30 */ s16  unk_30;
    /* 0x32 */ s16  unk_32;
    /* 0x34 */ char pad_34[0x04];
} Spr80039934;

typedef struct Wgt80039934 {
    /* 0x00 */ char          pad_00[0x28];
    /* 0x28 */ Spr80039934  *unk_28;
    /* 0x2C */ Spr80039934  *unk_2C;
    /* 0x30 */ Spr80039934  *unk_30;
    /* 0x34 */ char          pad_34[0x08];
    /* 0x3C */ s16           unk_3C;
    /* 0x3E */ u16           unk_3E;
    /* 0x40 */ s16           unk_40;
    /* 0x42 */ u16           unk_42;
} Wgt80039934;

extern void func_80039140(Wgt80039934 *);
extern void func_80036DBC(Wgt80039934 *);

void func_80039934(Wgt80039934 *wgt, s32 x, s32 y)
{
    Spr80039934 *spr;
    Spr80039934 *shadow;

    wgt->unk_3C = x;
    wgt->unk_40 = y;

    spr = wgt->unk_28;
    if (spr != NULL) {
        spr->unk_30 = x;
        spr->unk_32 = y;
    }

    spr = wgt->unk_2C;
    if (spr != NULL) {
        if (spr->unk_1E == 4) {
            func_80039140(wgt);
        } else {
            spr->unk_30 = x;
            spr->unk_32 = y;
        }
    }

    shadow = wgt->unk_30;
    if (shadow != NULL) {
        if (shadow->unk_1E == 4) {
            func_80036DBC(wgt);
        } else {
            shadow->unk_30 = wgt->unk_3E + x - 0x10;
            shadow->unk_32 = wgt->unk_42 + y - 0x10;
        }
    }
}
