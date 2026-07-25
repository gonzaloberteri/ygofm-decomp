#include "types.h"
#include "m2c_macros.h"

extern s32 D_8009AF64;
extern s32 D_8009AF68;

void func_8003FE70(s32 arg0) {
    D_8009AF68 = arg0;
    D_8009AF64 = arg0;
}
