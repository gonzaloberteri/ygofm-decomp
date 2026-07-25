/* decomp-flags: opt=-O2 as_G=0 cc1_extra=-fno-schedule-insns,-fno-schedule-insns2 */
#include "types.h"

extern void func_80040468(s32 *, s32, s32, s32, s32, s32);

void func_80042874(s32 *arg0, s32 arg1, s32 arg2, s32 arg3, s32 arg4, s32 arg5, s32 arg6)
{
    arg0[0x15] = arg6;
    func_80040468(arg0, arg1, arg2, arg3, arg4, arg5);
}
