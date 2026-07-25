#include "types.h"
#include "m2c_macros.h"

s32 func_80042960(void *arg0) {
    M2C_UNK (*temp_v0)();

    temp_v0 = M2C_FIELD(arg0, M2C_UNK (**)(), 0x24);
    if (temp_v0 != NULL) {
        temp_v0();
    }
    return (M2C_FIELD(arg0, u16 *, 8) & 0xC0) == 0xC0;
}
