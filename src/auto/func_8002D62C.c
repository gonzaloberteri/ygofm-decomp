#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B269;
extern u8 D_8009B26C;

M2C_UNK func_801683EC();                            /* extern */
s32 func_80169C08();                                /* extern */
void func_8002D62C();                               /* static */
M2C_UNK func_8003BBF8();                            /* static */

void func_8002D62C(void) {
    u8 temp_v1;

    temp_v1 = D_8009B26C;
    if (!(temp_v1 & 0x40)) {
        D_8009B26C = (u8) (temp_v1 | 0x40);
        func_8003BBF8();
        func_801683EC();
    }
    if (func_80169C08() != 0) {
        D_8009B26C = (u8) D_8009B269;
    }
}
