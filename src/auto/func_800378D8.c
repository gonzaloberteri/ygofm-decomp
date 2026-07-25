#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B328;

void func_800378D8(void *arg0);                     /* static */

void func_800378D8(void *arg0) {
    u8 temp_v1;

    temp_v1 = M2C_FIELD(arg0, u8 *, 0x51);
    if (!(temp_v1 & 0x80)) {
        M2C_FIELD(arg0, u8 *, 0x51) = (u8) (temp_v1 | 0x80);
    }
    if (M2C_FIELD(D_8009B328, u8 *, 0x33) == 0) {
        M2C_FIELD(arg0, u8 *, 0x51) = 0U;
    }
}
