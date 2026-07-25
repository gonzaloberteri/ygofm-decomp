#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B269;
extern u8 D_8009B26C;

M2C_UNK func_80015A00();                            /* static */
void func_8002D6C8();                               /* static */
M2C_UNK func_8003C2B4();                            /* static */
M2C_UNK func_8003C628();                            /* static */
s32 func_8003C8CC();                                /* static */
M2C_UNK func_8003FF34();                            /* static */

void func_8002D6C8(void) {
    u8 temp_v1;

    temp_v1 = D_8009B26C;
    if (!(temp_v1 & 0x40)) {
        D_8009B26C = (u8) (temp_v1 | 0x40);
        func_8003C2B4();
        func_8003C628();
        func_80015A00();
    }
    if (func_8003C8CC() == 0) {
        func_8003FF34();
        D_8009B26C = (u8) D_8009B269;
    }
}
