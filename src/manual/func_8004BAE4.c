/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8009B458 {
    u8  unk0000[0x7DC];
    u8 *unk07DC;
    u8  unk07E0[0xC];
    u32 unk07EC;
} Unk8009B458;

typedef struct Unk8004BAE4 {
    s32 unk00;
    u8  unk04[0x20];
    u8  unk24;
} Unk8004BAE4;

extern Unk8009B458 *D_8009B458;

s32 func_8004BAE4(Unk8004BAE4 *arg0)
{
    Unk8009B458 *g;
    s32 pos;
    u8 c;

    g = D_8009B458;
    pos = arg0->unk00;
    c = g->unk07DC[pos];
    pos++;
    arg0->unk00 = pos;
    if (g->unk07EC < (u32) pos) {
        arg0->unk24 = 1;
        return -1;
    }
    return c;
}
