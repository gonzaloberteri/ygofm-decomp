#include "types.h"
#include "m2c_macros.h"

extern s32 D_8009B074;
extern u8 D_8009B078;

s32 func_8005FB14(void) {
    s32 var_v1;

    var_v1 = 0;
    if (D_8009B078 != 0) {
        var_v1 = D_8009B074;
    }
    return var_v1;
}
