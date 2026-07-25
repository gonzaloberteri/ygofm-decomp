#include "types.h"
#include "m2c_macros.h"

extern s32 D_8009B304;
extern s32 D_8009B30C;
extern s32 D_8009B310;
extern s32 D_8009B314;

void func_80035680(s32 arg0) {
    D_8009B314 = 0;
    D_8009B310 = arg0;
    D_8009B304 = arg0;
    D_8009B30C = (s32) (D_8009B30C | 4);
}
