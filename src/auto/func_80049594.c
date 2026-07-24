#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B458;

void func_80049594(s32 arg0) {
    M2C_FIELD(D_8009B458, s32 *, 0x81C) = arg0;
}
