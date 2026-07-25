#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B3C1;
extern s8 D_8009B3EB;

M2C_UNK func_8003E854();                            /* static */
void func_8003EE90();                               /* static */

void func_8003EE90(void) {
    u8 temp_v1;

    temp_v1 = D_8009B3C1;
    if (!(temp_v1 & 0x80)) {
        D_8009B3C1 = (u8) (temp_v1 | 0x80);
        D_8009B3EB = 0;
    }
    func_8003E854();
}
