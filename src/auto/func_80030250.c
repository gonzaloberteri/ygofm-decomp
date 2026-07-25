#include "types.h"
#include "m2c_macros.h"

extern s8 D_8009B2B4;
extern s8 D_8009B2B5;
extern s8 D_8009B2B6;
extern s8 D_8009B2B8;
extern s8 D_8009B2C0;
extern s8 D_8009B2C1;
extern s8 D_8009B2C2;
extern s8 D_8009B2DC;
extern s8 D_8009B2E0;
extern s8 D_8009B2E9;
extern s8 D_8009B2EA;
extern s32 D_8009B2EC;

void func_80030250(s32 arg0, s8 arg1, s8 arg2, s8 arg3, s32 arg4, s32 arg5, s32 arg6) {
    D_8009B2EA = 0;
    D_8009B2EC = arg0;
    D_8009B2B4 = arg1;
    D_8009B2B5 = arg2;
    D_8009B2B6 = arg3;
    D_8009B2E9 = 0;
    D_8009B2DC = 0;
    D_8009B2B8 = (s8) arg4;
    D_8009B2C2 = (s8) arg5;
    D_8009B2C1 = (s8) arg5;
    D_8009B2C0 = (s8) arg5;
    D_8009B2E0 = (s8) arg6;
}
