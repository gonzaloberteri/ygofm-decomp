#include "types.h"
#include "m2c_macros.h"

s32 func_8004006C();                                /* static */
void *func_800400AC(s32, M2C_UNK);                  /* static */
M2C_UNK func_800404CC(void *, M2C_UNK, M2C_UNK, M2C_UNK, s32, s32, s32, s32); /* static */
M2C_UNK func_80042918(void *);                      /* static */

void *func_8002E3FC(void) {
    void *temp_v0;

    temp_v0 = func_800400AC(func_8004006C(), 2);
    func_800404CC(temp_v0, 0x10, 0xB0, 0, 0, 0, 0xD, 0x100);
    M2C_FIELD(temp_v0, u16 *, 8) = (u16) (M2C_FIELD(temp_v0, u16 *, 8) | 8);
    func_80042918(temp_v0);
    return temp_v0;
}
