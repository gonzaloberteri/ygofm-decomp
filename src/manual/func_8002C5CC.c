/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Slot {
    /* 0x00 */ s8 unk_00[0x1C];
    /* 0x1C */ u8 flags;
    /* 0x1D */ s8 unk_1D[3];
} Slot;

extern Slot D_800EAD88[8];

/* Returns the first slot whose bit 7 is clear, or NULL if all 8 are taken. */
Slot *func_8002C5CC(void)
{
    Slot *slot = D_800EAD88;
    s32 i = 8;

    do {
        if (slot->flags & 0x80) {
            slot++;
            continue;
        }
        return slot;
    } while (--i != 0);

    return NULL;
}
