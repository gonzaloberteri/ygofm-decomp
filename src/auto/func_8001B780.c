#include "types.h"
#include "m2c_macros.h"

void func_8001B780(void *arg0) {
    void *temp_v1;

    temp_v1 = M2C_FIELD(arg0, void **, 4);
    M2C_FIELD(temp_v1, s16 *, 0x30) = (s16) ((M2C_FIELD(arg0, s8 *, 0xE) * 0x3C) + 0xE);
    M2C_FIELD(temp_v1, s16 *, 0x32) = 0xC2;
}
