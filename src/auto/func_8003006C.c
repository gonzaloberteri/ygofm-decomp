#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B290;

s32 func_8003006C(void) {
    void *temp_v1;

    temp_v1 = D_8009B290;
    D_8009B290 = (void *) (temp_v1 + 2);
    return M2C_FIELD(temp_v1, u8 *, 0) | (M2C_FIELD(temp_v1, u8 *, 1) << 8);
}
