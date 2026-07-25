#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B328;

void func_80037950(void *arg0);                     /* static */

void func_80037950(void *arg0) {
    u8 temp_v1;
    void *temp_a1;

    temp_a1 = D_8009B328;
    temp_v1 = M2C_FIELD(temp_a1, u8 *, 0x32);
    if (!(temp_v1 & 3)) {
        M2C_FIELD(temp_a1, u8 *, 0x32) = (u8) (temp_v1 | 0x10);
        M2C_FIELD(D_8009B328, s8 *, 0x33) = 4;
        M2C_FIELD(arg0, s8 *, 0x51) = 8;
    }
}
