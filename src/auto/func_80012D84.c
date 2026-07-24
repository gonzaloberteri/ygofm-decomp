#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_80012D4C();                            /* static */

void func_80012D84(s32 arg0) {
    s32 var_s0;

    var_s0 = arg0;
    do {
        var_s0 -= 1;
        func_80012D4C();
    } while (var_s0 != 0);
}
