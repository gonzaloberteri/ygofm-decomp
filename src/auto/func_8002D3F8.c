#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B26C;

M2C_UNK func_80168FB4();                            /* extern */
M2C_UNK func_80015A00();                            /* static */
void func_8002D3F8();                               /* static */
M2C_UNK func_8003B9BC();                            /* static */
M2C_UNK func_8003FF34();                            /* static */

void func_8002D3F8(void) {
    u8 temp_v1;

    temp_v1 = D_8009B26C;
    if (!(temp_v1 & 0x40)) {
        D_8009B26C = (u8) (temp_v1 | 0x40);
        func_8003B9BC();
        func_80015A00();
    }
    func_80168FB4();
    if (!(D_8009B26C & 0x40)) {
        func_8003FF34();
    }
}
