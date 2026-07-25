#include "types.h"
#include "m2c_macros.h"

void func_8004044C(void *arg0, s8 arg1, s8 arg2, s8 arg3) {
    M2C_FIELD(arg0, s8 *, 0x67) = arg1;
    M2C_FIELD(arg0, s8 *, 0x68) = arg2;
    M2C_FIELD(arg0, s8 *, 0x69) = arg3;
    M2C_FIELD(arg0, u16 *, 8) = (u16) (M2C_FIELD(arg0, u16 *, 8) & 0xFFEF);
}
