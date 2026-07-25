#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B45C;

u8 func_80047008(void) {
    return M2C_FIELD(D_8009B45C, u8 *, 0x48);
}
