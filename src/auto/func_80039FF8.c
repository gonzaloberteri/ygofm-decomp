#include "types.h"
#include "m2c_macros.h"

void func_80039FF8(void *arg0);                     /* static */

void func_80039FF8(void *arg0) {
    u8 temp_v1;

    temp_v1 = M2C_FIELD(arg0, u8 *, 0x32);
    if (!(temp_v1 & 3)) {
        M2C_FIELD(arg0, u8 *, 0x32) = (u8) (temp_v1 | 0x10);
        M2C_FIELD(arg0, s8 *, 0x33) = 0;
    }
}
