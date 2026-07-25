#include "types.h"
#include "m2c_macros.h"

s32 func_80036D3C();                                /* static */
void func_80038690();                               /* static */
M2C_UNK func_8003FF08(s32);                         /* static */

void func_80038690(void) {
    func_8003FF08(func_80036D3C() & 0xFFFF);
}
