#include "types.h"
#include "m2c_macros.h"

extern u16 D_8009B398;

s32 func_8003B734(void) {
    return D_8009B398 & 0xC0;
}
