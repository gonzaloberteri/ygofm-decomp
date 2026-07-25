#include "types.h"
#include "m2c_macros.h"

extern s8 D_8009B3C0;
extern u8 D_8009B3ED;

M2C_UNK func_8003F8D4();                            /* static */

void func_8003FCD8(void) {
    u8 temp_v1;

    temp_v1 = D_8009B3ED;
    if (!(temp_v1 & 0x80)) {
        D_8009B3ED = (u8) (temp_v1 | 0x80);
        D_8009B3C0 = 0x29;
    }
    func_8003F8D4();
}
