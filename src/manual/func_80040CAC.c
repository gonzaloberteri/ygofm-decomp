/* decomp-flags: opt=-O2 as_G=0 cc1_G=0 */
#include "types.h"
typedef struct Rec70 {
    u8  unk_00[2];
    s16 unk_02;
    u8  unk_04[0x24 - 0x04];
    void (*unk_24)(struct Rec70 *);
    u8  unk_28[0x70 - 0x28];
} Rec70;
extern s16 D_800EFE38;
extern Rec70 D_800EFE48[];
void func_80040CAC(void)
{
    s16 i = D_800EFE38;
    Rec70 *p;
    void (*fn)(Rec70 *);

    while (i >= 0) {
        p = &D_800EFE48[i];
        fn = p->unk_24;
        i = p->unk_02;
        if (fn != NULL) {
            fn(p);
        }
    }
}
