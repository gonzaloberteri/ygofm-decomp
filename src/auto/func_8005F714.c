#include "types.h"
#include "m2c_macros.h"

extern s8 D_8009B07A;
extern u8 D_8009B07B;
extern u8 D_8009B07C;

M2C_UNK D_80091550();                               /* static */
M2C_UNK func_8005F91C(s32, void *, void *, M2C_UNK); /* static */

void func_8005F714(s32 arg0, s32 arg1, M2C_UNK arg2) {
    s32 var_a0;
    s8 temp_a0_2;
    u8 temp_a0;
    void *var_a2;
    void *var_t0;

    if (arg0 >= 0) {
        var_t0 = (arg0 * 8) + D_80091550;
    } else {
        var_t0 = NULL;
    }
    if (arg1 >= 0) {
        var_a2 = (arg1 * 8) + D_80091550;
    } else {
        var_a2 = NULL;
    }
    temp_a0 = D_8009B07B;
    if ((temp_a0 != 1) || (D_8009B07C != temp_a0)) {
        temp_a0_2 = D_8009B07A;
        if (temp_a0_2 < 0) {
            var_a0 = 0;
        } else {
            D_8009B07A = (s8) ((u8) D_8009B07A + 1);
            var_a0 = temp_a0_2 > 0;
        }
        func_8005F91C(var_a0, var_t0, var_a2, arg2);
    }
}
