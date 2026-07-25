#include "types.h"
#include "m2c_macros.h"

extern s32 D_8009B350;

void func_80038D14(void *arg0);                     /* static */

void func_80038D14(void *arg0) {
    M2C_FIELD(arg0, s8 *, 0x51) = 4;
    D_8009B350 = 1;
}
