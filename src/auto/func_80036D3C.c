#include "types.h"
#include "m2c_macros.h"

s32 func_80036D3C(void *arg0) {
    void **temp_a0;
    void *temp_v1;

    temp_a0 = arg0 + (M2C_FIELD(arg0, s8 *, 0x58) * 4);
    temp_v1 = *temp_a0;
    *temp_a0 = temp_v1 + 2;
    return M2C_FIELD(temp_v1, u8 *, 0) | (M2C_FIELD(temp_v1, u8 *, 1) << 8);
}
