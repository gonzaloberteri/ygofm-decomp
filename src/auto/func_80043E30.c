#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_80073840();                            /* static */
M2C_UNK func_80073940(M2C_UNK);                     /* static */

void func_80043E30(s32 arg0) {
    InitCARD(arg0);
    StartCARD();
    func_80073940(0);
    func_80073840();
}
