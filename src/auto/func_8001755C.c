#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_800530C4();                            /* static */
M2C_UNK func_800533D8();                            /* static */
M2C_UNK func_80056250(M2C_UNK, s32, M2C_UNK, M2C_UNK); /* static */
extern s32 D_80010000;

void func_8001755C(void) {
    func_800530C4();
    func_800533D8();
    func_80056250(2, D_80010000, 0x63000, 4);
}
