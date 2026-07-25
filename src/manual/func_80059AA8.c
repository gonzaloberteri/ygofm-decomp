/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Entry {
    /* 0x0000 */ s8 unk_0000[0xE12];
    /* 0x0E12 */ u8 unk_0E12;
    /* 0x0E13 */ s8 unk_0E13[0xD];
} Entry; /* size 0xE20 */

extern Entry D_800F2C40[];

/* Reads unk_0E12 out of entry `index`, replacing it first if `value` >= 0. */
s32 func_80059AA8(s32 index, s32 value)
{
    Entry *base = D_800F2C40;
    Entry *entry = base + index;
    u8 prev = entry->unk_0E12;

    if (value >= 0) {
        entry->unk_0E12 = value;
    }
    return prev;
}
