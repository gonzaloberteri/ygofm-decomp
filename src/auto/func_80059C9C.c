#include "types.h"
#include "m2c_macros.h"

extern s8 D_8009AF94;
extern s8 D_8009AF9A;

M2C_UNK func_800530C4();                            /* static */
M2C_UNK func_800533D8();                            /* static */

void func_80059C9C(void) {
    func_800533D8();
    func_800530C4();
    D_8009AF94 = 0x14;
    D_8009AF9A = -1;
}
