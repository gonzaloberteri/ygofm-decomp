/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk800374A8 {
    /* 0x00 */ u8 unk00[0x51];
    /* 0x51 */ u8 unk51;
} Unk800374A8;

extern void func_800373C8(Unk800374A8 *, s32, s32);

void func_800374A8(Unk800374A8 *arg0)
{
    if ((arg0->unk51 & 0x80) == 0) {
        arg0->unk51 |= 0x80;
        func_800373C8(arg0, 3, 0);
        arg0->unk51 = 0x82;
    }
}
