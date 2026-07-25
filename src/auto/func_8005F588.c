#include "types.h"
#include "m2c_macros.h"

extern s8 D_8009B07A;
extern u8 D_8009B07B;
extern u8 D_8009B07C;

void func_8005F588(s32 arg0) {
    u8 temp_v1;

    temp_v1 = D_8009B07B;
    if ((temp_v1 != 1) || (D_8009B07C != temp_v1)) {
        if (arg0 == 0) {
            D_8009B07A = -1;
            return;
        }
        D_8009B07A = 0;
    }
}
