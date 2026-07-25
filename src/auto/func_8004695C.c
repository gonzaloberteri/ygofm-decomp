#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B458;

void func_8004695C(u8 arg0) {
    void *temp_v1;

    M2C_FIELD(D_8009B458, u8 *, 0x509) = arg0;
    temp_v1 = D_8009B458;
    if (M2C_FIELD(temp_v1, u8 *, 0x509) != 0) {
        M2C_FIELD(temp_v1, s8 *, 0x500) = 1;
        return;
    }
    M2C_FIELD(temp_v1, s8 *, 0x500) = 0;
}
