#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B26C;

M2C_UNK func_8016A080();                            /* extern */
M2C_UNK func_8016A37C();                            /* extern */
void func_8002D684();                               /* static */
M2C_UNK func_8003BEB8();                            /* static */

void func_8002D684(void) {
    u8 temp_v1;

    temp_v1 = D_8009B26C;
    if (!(temp_v1 & 0x40)) {
        D_8009B26C = (u8) (temp_v1 | 0x40);
        func_8003BEB8();
        func_8016A080();
    }
    func_8016A37C();
}
