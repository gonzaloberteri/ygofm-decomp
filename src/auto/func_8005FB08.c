#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B078;

s32 func_8005FB08(void) {
    return D_8009B078 == 0;
}
