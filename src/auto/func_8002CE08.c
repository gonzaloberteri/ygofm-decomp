#include "types.h"
#include "m2c_macros.h"

extern s8 D_8009B269;
extern u8 D_8009B26C;

void func_8002CE08();                               /* static */
M2C_UNK func_80030198();                            /* static */
M2C_UNK func_80031084();                            /* static */

void func_8002CE08(void) {
    u8 temp_v1;

    temp_v1 = D_8009B26C;
    if (!(temp_v1 & 0x40)) {
        D_8009B26C = (u8) (temp_v1 | 0x40);
        func_80030198();
        return;
    }
    func_80031084();
    if (!(D_8009B26C & 0x40)) {
        D_8009B269 = 0;
    }
}
