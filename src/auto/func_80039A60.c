#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_800393B0(void *);                      /* static */

void func_80039A60(void *arg0) {
    M2C_FIELD(arg0, u16 *, 0x34) = (u16) (M2C_FIELD(arg0, u16 *, 0x34) | 0xA00);
    do {
        func_800393B0(arg0);
    } while (!(M2C_FIELD(arg0, u16 *, 0x34) & 0x2000));
}
