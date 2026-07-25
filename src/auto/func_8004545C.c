#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_8004544C();                            /* static */
extern M2C_UNK (*D_8009B128)();
extern void *D_8009B45C;

void func_8004545C(void) {
    M2C_FIELD(D_8009B45C, s8 *, 0x1618) = 1;
    D_8009B128 = func_8004544C;
}
