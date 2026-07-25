#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B45C;

s16 func_80044FE4(void) {
    return M2C_FIELD(D_8009B45C, s16 *, 0x510);
}
