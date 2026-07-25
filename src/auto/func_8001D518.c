#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B1F8;

M2C_UNK func_80015DB8();                            /* static */
s32 func_8004002C();                                /* static */
void *func_800400AC(s32, M2C_UNK);                  /* static */
M2C_UNK func_80040468(void *, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32); /* static */
M2C_UNK func_800428EC(void *, M2C_UNK);             /* static */

void *func_8001D518(void *arg0) {
    void *var_s0;

    var_s0 = D_8009B1F8;
    if (var_s0 == NULL) {
        var_s0 = func_800400AC(func_8004002C(), 2);
        func_80040468(var_s0, 4, 3, 8, 0xB, 0x1F0);
        M2C_FIELD(var_s0, u8 *, 0x6A) = (u8) M2C_FIELD(arg0, u8 *, 0xA);
        func_800428EC(var_s0, 1);
        M2C_FIELD(var_s0, M2C_UNK (**)(), 0x24) = func_80015DB8;
        M2C_FIELD(var_s0, u16 *, 8) = (u16) (M2C_FIELD(var_s0, u16 *, 8) | 8);
    }
    return var_s0;
}
