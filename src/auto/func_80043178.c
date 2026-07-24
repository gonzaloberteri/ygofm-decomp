#include "types.h"
#include "m2c_macros.h"

void func_80043178(void *arg0) {
    M2C_FIELD(arg0, u16 *, 0x36) = (u16) M2C_FIELD(arg0, u16 *, 0x30);
    M2C_FIELD(arg0, u16 *, 0x38) = (u16) M2C_FIELD(arg0, u16 *, 0x32);
}
