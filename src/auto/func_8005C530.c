#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_8005BB7C(M2C_UNK);                     /* static */
s32 func_8005BE3C();                                /* static */

s32 func_8005C530(void) {
    s32 temp_v0;

    temp_v0 = func_8005BE3C();
    if (temp_v0 != 0) {
        func_8005BB7C(0);
    }
    return temp_v0;
}
