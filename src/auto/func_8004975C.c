#include "types.h"
#include "m2c_macros.h"

s32 func_80077150(s32, s32);                        /* static */
extern void *D_8009B458;

s16 func_8004975C(s32 arg0, s16 arg1) {
    s16 temp_s1;
    void *temp_s0;

    temp_s1 = M2C_FIELD(D_8009B458, s16 *, 0x4A4);
    if (temp_s1 == arg1) {
        temp_s0 = D_8009B458 + 0x4A4;
        SpuSetTransferStartAddr(M2C_FIELD(temp_s0, u32 *, 0x14));
        if (func_80077150(arg0, M2C_FIELD(temp_s0, s32 *, 0x10)) == M2C_FIELD(temp_s0, s32 *, 0x10)) {
            M2C_FIELD(temp_s0, s32 *, 0xC) = arg0;
            return temp_s1;
        }
        /* Duplicate return node #4. Try simplifying control flow for better match */
        return -1;
    }
    return -1;
}
