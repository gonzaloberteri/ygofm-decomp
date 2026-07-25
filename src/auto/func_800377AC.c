#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B357;

void func_800377AC(void *arg0);                     /* static */

void func_800377AC(void *arg0) {
    if (D_8009B357 == 0) {
        M2C_FIELD(arg0, s8 *, 0x51) = 0;
    }
}
