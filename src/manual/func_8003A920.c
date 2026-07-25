/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8003A920 {
    u8  unk00[0x30];
    s16 unk30;
    s16 unk32;
} Unk8003A920;

void func_8003A920(Unk8003A920 **arg0, s32 arg1, s32 arg2)
{
    s32 i;

    for (i = 2; i >= 0; i--) {
        if (arg0[i] != NULL) {
            arg0[i]->unk30 = arg1;
            arg0[i]->unk32 = arg2;
        }
    }
}
