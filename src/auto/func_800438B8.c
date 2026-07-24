#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_80012D4C();                            /* static */
extern s32 D_8009B0F4;
extern s32 D_8009B134;
extern u16 D_8009B398;

void func_800438B8(s32 arg0) {
    s32 var_s0;
    s32 var_s1;

    var_s0 = arg0;
    var_s1 = 0;
    do {
loop_1:
        func_80012D4C();
        if ((var_s1 == 0) && (((D_8009B0F4 & 0x02000030) | D_8009B134) == 0)) {
            var_s1 = 1;
        }
        if (D_8009B398 & 0x8C0) {
            var_s0 -= 1;
            if (var_s1 != 0) {
                var_s0 = 0;
                goto block_7;
            }
        } else {
block_7:
            var_s0 -= 1;
        }
        if (var_s0 >= 0) {
            goto loop_1;
        }
        var_s0 = 0;
    } while (var_s1 == 0);
}
