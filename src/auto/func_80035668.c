#include "types.h"
#include "m2c_macros.h"

extern s32 D_8009B300;
extern s32 D_8009B30C;

void func_80035668(s32 arg0) {
    D_8009B30C = arg0;
    D_8009B300 = 0x808080;
}
