#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_8004AAFC();                            /* static */
M2C_UNK func_8004C84C();                            /* static */
M2C_UNK func_8004C8C8();                            /* static */
extern void *D_8009B458;

void func_8004B9E0(void) {
    if (M2C_FIELD(D_8009B458, u8 *, 0x501) == 0) {
        M2C_FIELD(D_8009B458, u8 *, 0x501) = 1U;
        if (M2C_FIELD(D_8009B458, u8 *, 0x502) != 0) {
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
            func_8004C8C8();
        }
        func_8004C84C();
        func_8004AAFC();
        M2C_FIELD(D_8009B458, u8 *, 0x501) = 0U;
    }
}
