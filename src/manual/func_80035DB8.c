/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Record {
    /* 0x00 */ s8 unk_00[0x11];
    /* 0x11 */ u8 unk_11;
    /* 0x12 */ u8 unk_12;
    /* 0x13 */ s8 unk_13[9];
} Record; /* size 0x1C */

extern Record D_800EB288[620];

/* Clears unk_11 on every record tagged with arg0 + 1. */
void func_80035DB8(s32 arg0)
{
    s32 n = 620;
    s32 key = arg0 + 1;
    s32 i = 0;

    do {
        if (D_800EB288[i].unk_12 == key) {
            D_800EB288[i].unk_11 = 0;
        }
        i++;
    } while (--n != 0);
}
