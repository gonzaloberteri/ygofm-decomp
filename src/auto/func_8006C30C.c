#include "types.h"
#include "m2c_macros.h"

void func_8006C30C(void *arg0, void *arg1) {
    M2C_FIELD(arg0, u8 *, 0) = (u8) M2C_FIELD(arg1, u8 *, 0);
    M2C_FIELD(arg0, u8 *, 1) = (u8) M2C_FIELD(arg1, u8 *, 1);
    M2C_FIELD(arg0, u8 *, 2) = (u8) M2C_FIELD(arg1, u8 *, 2);
}
