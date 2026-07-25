/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct Unk8003A95C {
    /* 0x00 */ u8  unk00[0x34];
    /* 0x34 */ s16 unk34;
    /* 0x36 */ s16 unk36;
} Unk8003A95C;

extern void func_8003A920(Unk8003A95C *, s32, s32);

void func_8003A95C(Unk8003A95C *arg0, s32 arg1, s32 arg2)
{
    arg0->unk34 = arg1;
    arg0->unk36 = arg2;
    func_8003A920(arg0, arg0->unk34, arg0->unk36);
}
