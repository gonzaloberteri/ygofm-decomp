#include "types.h"
#include "m2c_macros.h"

s32 DsRead2(s32, M2C_UNK);                          /* static */
s32 func_8007E7F0(M2C_UNK, s32, M2C_UNK);           /* static */

void func_8005C62C(s32 arg0) {
    do {

    } while (func_8007E7F0(2, arg0, 0) == 0);
    do {

    } while (func_8007E7F0(0x16, arg0, 0) == 0);
    do {

    } while (DsRead2(arg0, 0x1E0) == 0);
}
