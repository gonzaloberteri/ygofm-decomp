#include "types.h"
#include "m2c_macros.h"

void func_800427DC(void *arg0, s8 arg1) {
    M2C_FIELD(arg0, s32 *, 0x54) = 0;
    M2C_FIELD(arg0, s32 *, 0x4C) = 0;
    M2C_FIELD(arg0, s32 *, 0x44) = 0;
    M2C_FIELD(arg0, s32 *, 0x3C) = 0;
    M2C_FIELD(arg0, s32 *, 0x34) = 0;
    M2C_FIELD(arg0, s32 *, 0x2C) = 0;
    M2C_FIELD(arg0, s32 *, 0x10) = 0;
    M2C_FIELD(arg0, s8 *, 0x21) = 0;
    M2C_FIELD(arg0, s8 *, 0x20) = 0;
    M2C_FIELD(arg0, s8 *, 0x22) = 0;
    M2C_FIELD(arg0, s16 *, 0x1C) = 0;
    M2C_FIELD(arg0, s16 *, 0x1A) = 0;
    M2C_FIELD(arg0, s16 *, 0x18) = 0;
    M2C_FIELD(arg0, s8 *, 0x5A) = arg1;
    M2C_FIELD(arg0, u16 *, 8) = (u16) (M2C_FIELD(arg0, u16 *, 8) | 8);
}
