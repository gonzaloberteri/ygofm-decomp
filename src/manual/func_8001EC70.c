/* decomp-flags: opt=-Os as_G=8 cc1_G=0 expand_div=1 */
#include "types.h"

/* Reached through func_80042B98, which treats +0x6C as a u8 whose bit 7 is a
 * "already stepped this frame" latch.  Note this record disagrees with
 * game.h's Obj800EFE48 at 0x24/0x28/0x2C/0x6C -- here 0x28..0x2E are halfwords
 * and 0x6C is a byte -- so it is declared locally rather than shared. */
typedef struct Ent8001EC70 {
    /* 0x00 */ char pad_00[0x24];
    /* 0x24 */ s32  unk_24;
    /* 0x28 */ s16  unk_28;
    /* 0x2A */ s16  unk_2A;
    /* 0x2C */ s16  unk_2C;
    /* 0x2E */ s16  unk_2E;
    /* 0x30 */ char pad_30[0x30];
    /* 0x60 */ s16  unk_60;
    /* 0x62 */ char pad_62[0x0A];
    /* 0x6C */ u8   unk_6C;
} Ent8001EC70;

extern s32 func_80042B98(Ent8001EC70 *);
extern void func_80043178(Ent8001EC70 *);
extern void func_8004318C(Ent8001EC70 *, s16, s16, s16);

void func_8001EC70(Ent8001EC70 *e)
{
    if (func_80042B98(e) == 0) {
        func_80043178(e);
        e->unk_60 = 0;
        e->unk_2E = 0;
    }
    func_8004318C(e, e->unk_28, e->unk_2A, e->unk_60);
    e->unk_60 += 0x800 / e->unk_2C;
    if (e->unk_60 >= 0x800) {
        e->unk_6C = 0;
        e->unk_24 = 0;
    }
}
