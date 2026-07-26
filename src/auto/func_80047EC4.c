#include "types.h"
#include "m2c_macros.h"

M2C_UNK SpuGetAllKeysStatus(void *);                /* static */
M2C_UNK SpuSetKey(M2C_UNK, M2C_UNK);                /* static */
extern void *D_8009B45C;

void func_80047EC4(void) {
    s32 var_s0;
    u8 temp_a0;

    var_s0 = 0;
loop_1:
    SpuSetKey(0, 0xF00000);
    SpuGetAllKeysStatus(D_8009B45C + 0x15D8);
    temp_a0 = M2C_FIELD(D_8009B45C, u8 *, 0x15EF);
    var_s0 += 1;
    if ((temp_a0 + M2C_FIELD(D_8009B45C, u8 *, 0x15ED) + M2C_FIELD(D_8009B45C, u8 *, 0x15EE) + temp_a0) != 0) {
        if (var_s0 < 0x18) {
            goto loop_1;
        }
    }
}
