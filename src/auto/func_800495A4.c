#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_8004B9E0();                            /* static */
extern void *D_8009B458;

void func_800495A4(void) {
    if (M2C_FIELD(D_8009B458, u8 *, 0x814) != 0) {
        func_8004B9E0();
    }
}
