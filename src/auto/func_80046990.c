#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B45C;

void func_80046990(s32 arg0, s32 arg1, s32 arg2) {
    void *temp_v1;
    void *temp_v1_2;
    void *temp_v1_3;
    void *temp_v1_4;

    temp_v1 = D_8009B45C;
    M2C_FIELD(temp_v1, s32 *, 0x3C) = 0;
    if (arg0 == 0) {
        M2C_FIELD(temp_v1, u8 *, 0x4A) = (u8) (M2C_FIELD(temp_v1, u8 *, 0x4A) & 0xFE);
    }
    if (arg1 == 0) {
        temp_v1_2 = D_8009B45C;
        M2C_FIELD(temp_v1_2, u8 *, 0x4A) = (u8) (M2C_FIELD(temp_v1_2, u8 *, 0x4A) & 0xFD);
    }
    if (arg2 == 0) {
        temp_v1_3 = D_8009B45C;
        M2C_FIELD(temp_v1_3, u8 *, 0x4A) = (u8) (M2C_FIELD(temp_v1_3, u8 *, 0x4A) & 0xBF);
    }
    temp_v1_4 = D_8009B45C;
    M2C_FIELD(temp_v1_4, u16 *, 0x40) = (u16) (M2C_FIELD(temp_v1_4, u16 *, 0x40) | 0xA);
}
