/* decomp-flags: opt=-Os as_G=8 */
#include "types.h"

/* Re-parents an object to the anchor named by its unk_2C slot, in the table
 * row selected by D_8009B1D5.  With no anchor it falls back to func_8004036C. */

typedef struct Obj80022EEC {
    /* 0x00 */ char pad_00[0x24];
    /* 0x24 */ s32  unk_24;
    /* 0x28 */ u16  unk_28;
    /* 0x2A */ u16  unk_2A;
    /* 0x2C */ s16  unk_2C;
    /* 0x2E */ char pad_2E[0x02];
    /* 0x30 */ u16  unk_30;
    /* 0x32 */ u16  unk_32;
    /* 0x34 */ char pad_34[0x38];
    /* 0x6C */ u8   unk_6C;
    /* 0x6D */ char pad_6D[0x03];
} Obj80022EEC;                       /* size 0x70 */

typedef struct Anchor80022EEC {
    /* 0x00 */ Obj80022EEC *unk_00;
    /* 0x04 */ char         pad_04[0x18];
} Anchor80022EEC;                    /* size 0x1C */

extern Anchor80022EEC D_800E9F10[][4];
extern u8 D_8009B1D5;                /* gp + 0x2CD */

extern void func_8004036C(Obj80022EEC *);

void func_80022EEC(Obj80022EEC *obj)
{
    Obj80022EEC *anchor;

    anchor = D_800E9F10[D_8009B1D5][obj->unk_2C].unk_00;
    if (anchor == NULL) {
        func_8004036C(obj);
        return;
    }

    obj->unk_30 = anchor->unk_30 + obj->unk_28;
    obj->unk_32 = anchor->unk_32 + obj->unk_2A;
    if (anchor->unk_6C == 0) {
        obj->unk_6C = 0;
        obj->unk_24 = 0;
    }
}
