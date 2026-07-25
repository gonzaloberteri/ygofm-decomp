#include "types.h"
#include "m2c_macros.h"

void func_800379C4(void *arg0);                     /* static */
s32 func_80049120();                                /* static */

void func_800379C4(void *arg0) {
    if (func_80049120() != 1) {
        M2C_FIELD(arg0, s8 *, 0x51) = 0;
    }
}
