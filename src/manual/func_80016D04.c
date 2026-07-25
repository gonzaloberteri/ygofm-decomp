/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk80016D04 {
    u8  unk00[0x30];
    s16 unk30;
    s16 unk32;
} Unk80016D04;

extern void func_80016784(Unk80016D04 *, s32, s32, s32);

void func_80016D04(Unk80016D04 *arg0, s32 arg1)
{
    func_80016784(arg0, arg1, arg0->unk30, arg0->unk32);
}
