#include "types.h"
#include "m2c_macros.h"

void func_800389C4(void *arg0);                     /* static */

void func_800389C4(void *arg0) {
    M2C_FIELD(arg0, u16 *, 0x34) = (u16) (M2C_FIELD(arg0, u16 *, 0x34) & 0xFFF7);
}
