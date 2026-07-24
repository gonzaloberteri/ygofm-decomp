#include "types.h"
#include "m2c_macros.h"

void func_80040410(void *arg0, s8 arg1) {
    M2C_FIELD(arg0, s8 *, 0x69) = arg1;
    M2C_FIELD(arg0, u16 *, 8) = (u16) (M2C_FIELD(arg0, u16 *, 8) & 0xFFEF);
}
