#include "types.h"
#include "m2c_macros.h"

void func_80042824(void *arg0, s8 arg1) {
    M2C_FIELD(arg0, s32 *, 0x68) = 0x808080;
    M2C_FIELD(arg0, s32 *, 0x5C) = 0x808080;
    M2C_FIELD(arg0, s32 *, 0x50) = 0x808080;
    M2C_FIELD(arg0, s32 *, 0x44) = 0x808080;
    M2C_FIELD(arg0, s32 *, 0x38) = 0x808080;
    M2C_FIELD(arg0, s32 *, 0x2C) = 0x808080;
    M2C_FIELD(arg0, s32 *, 0x10) = 0;
    M2C_FIELD(arg0, s8 *, 0x21) = 0;
    M2C_FIELD(arg0, s8 *, 0x20) = 0;
    M2C_FIELD(arg0, s8 *, 0x22) = 0;
    M2C_FIELD(arg0, s16 *, 0x1C) = 0;
    M2C_FIELD(arg0, s16 *, 0x1A) = 0;
    M2C_FIELD(arg0, s16 *, 0x18) = 0;
    M2C_FIELD(arg0, s8 *, 0x72) = arg1;
    M2C_FIELD(arg0, u16 *, 8) = (u16) (M2C_FIELD(arg0, u16 *, 8) | 8);
}
