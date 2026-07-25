#include "types.h"
#include "m2c_macros.h"

s32 func_800181EC(void *arg0) {
    s32 var_a1;
    u8 temp_v1;

    temp_v1 = M2C_FIELD(arg0, u8 *, 0x68);
    var_a1 = 1;
    switch (temp_v1) {                              /* irregular */
    case 23:
    case 20:
        var_a1 = 2;
        break;
    case 21:
        var_a1 = 3;
        break;
    case 22:
        var_a1 = 4;
        break;
    }
    if (M2C_FIELD(arg0, u8 *, 0x22) != 0) {
        var_a1 |= 0x80;
    }
    return var_a1;
}
