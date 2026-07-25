#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B45C;

s16 func_8004703C(void) {
    return M2C_FIELD(D_8009B45C, s16 *, 0x40);
}
