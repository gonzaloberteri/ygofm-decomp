#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B45C;

void func_8004701C(s32 arg0) {
    void *temp_v1;

    temp_v1 = D_8009B45C;
    M2C_FIELD(temp_v1, u8 *, 0x4A) = (u8) ((M2C_FIELD(temp_v1, u8 *, 0x4A) & 0xF0) | arg0);
}
