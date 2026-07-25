#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B328;

void func_8003787C(void *arg0);                     /* static */
M2C_UNK func_80039FD4(void *);                      /* static */

void func_8003787C(void *arg0) {
    u8 temp_v1;
    void *temp_a0;

    temp_v1 = M2C_FIELD(arg0, u8 *, 0x51);
    if (!(temp_v1 & 0x80)) {
        M2C_FIELD(arg0, u8 *, 0x51) = (u8) (temp_v1 | 0x80);
    }
    temp_a0 = D_8009B328;
    if (M2C_FIELD(temp_a0, u8 *, 0x33) == 0) {
        func_80039FD4(temp_a0);
        M2C_FIELD(arg0, u8 *, 0x51) = 0U;
    }
}
