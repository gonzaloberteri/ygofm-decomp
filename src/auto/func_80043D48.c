#include "types.h"
#include "m2c_macros.h"

extern s32 D_8009B450;

M2C_UNK func_80073880(s32);                         /* static */

void func_80043D48(void *arg0) {
    func_80073880(M2C_FIELD(arg0, s32 *, 0));
    func_80073880(M2C_FIELD(arg0, s32 *, 4));
    func_80073880(M2C_FIELD(arg0, s32 *, 8));
    func_80073880(M2C_FIELD(arg0, s32 *, 0xC));
    D_8009B450 = -1;
}
