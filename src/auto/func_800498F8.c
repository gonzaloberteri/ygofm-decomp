#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B458;

void func_800498F8(void) {
    if (M2C_FIELD(D_8009B458, s16 *, 0x4A4) != -1) {
        M2C_FIELD(D_8009B458, s16 *, 0x4A4) = -1;
    }
}
