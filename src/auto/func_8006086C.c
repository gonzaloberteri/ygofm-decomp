#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_80060170(s32, s32);                    /* static */
s32 func_8006041C(s32);                             /* static */

void func_8006086C(void *arg0) {
    *M2C_FIELD(arg0, s32 **, 4) = func_8006041C(M2C_FIELD(arg0, s32 *, 0));
    func_80060170(M2C_FIELD(arg0, s32 *, 0), *M2C_FIELD(arg0, s32 **, 4));
}
