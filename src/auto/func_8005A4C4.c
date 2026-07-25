#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_8005922C(void *, M2C_UNK);             /* static */

void func_8005A4C4(void *arg0, s32 arg1, s32 arg2, s32 arg3, s32 arg4) {
    void *temp_v0;

    temp_v0 = M2C_FIELD(arg0, void **, 0xD18);
    if (temp_v0 != NULL) {
        M2C_FIELD(temp_v0, s16 *, 0x44) = 0;
        M2C_FIELD(M2C_FIELD(arg0, void **, 0xD18), s16 *, 0x46) = (s16) arg4;
        M2C_FIELD(M2C_FIELD(arg0, void **, 0xD18), s16 *, 0x48) = 0;
        M2C_FIELD(M2C_FIELD(arg0, void **, 0xD18), s32 *, 0x18) = arg1;
        M2C_FIELD(M2C_FIELD(arg0, void **, 0xD18), s32 *, 0x1C) = arg2;
        M2C_FIELD(M2C_FIELD(arg0, void **, 0xD18), s32 *, 0x20) = arg3;
    }
    func_8005922C(M2C_FIELD(arg0, void **, 0xD18), 0);
}
