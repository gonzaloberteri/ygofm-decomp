#include "types.h"
#include "m2c_macros.h"

extern u16 D_8009AF7A;

void func_8004293C(void *arg0) {
    M2C_FIELD(arg0, s8 *, 0x17) = 3;
    M2C_FIELD(arg0, s16 *, 0x14) = (s16) (D_8009AF7A - (s8) M2C_FIELD(arg0, u8 *, 0x16));
}
