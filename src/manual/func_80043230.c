/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

/* One record of the 0x70-byte object pool at D_800EFE48 (see include/game.h,
 * section 3).  Only the four halfwords this function touches are named. */
typedef struct Obj80043230 {
    /* 0x00 */ char pad_00[0x30];
    /* 0x30 */ s16  unk_30;
    /* 0x32 */ s16  unk_32;
    /* 0x34 */ char pad_34[0x02];
    /* 0x36 */ s16  unk_36;
    /* 0x38 */ s16  unk_38;
    /* 0x3A */ char pad_3A[0x36];
} Obj80043230;                       /* size 0x70 */

extern s32 rsin(s32);

void func_80043230(Obj80043230 *obj, s32 cx, s32 cy, s32 ang)
{
    s32 dx;
    s32 dy;
    s32 c;

    dx = obj->unk_36 - cx;
    dy = obj->unk_38 - cy;

    if (ang < 0) {
        c = rsin(ang + 0x400);
        obj->unk_30 = obj->unk_36 - dx * c / 0x1000;
        obj->unk_32 = obj->unk_38 - dy * c / 0x1000;
    } else {
        c = -rsin(ang);
        obj->unk_30 = cx - dx * c / 0x1000;
        obj->unk_32 = cy - dy * c / 0x1000;
    }
}
