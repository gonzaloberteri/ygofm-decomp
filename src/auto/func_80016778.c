#include "types.h"
#include "m2c_macros.h"

void func_80016778(void *arg0, u32 arg1) {
    M2C_FIELD(arg0, s8 *, 0x69) = (s8) (arg1 >> 0x1F);
}
