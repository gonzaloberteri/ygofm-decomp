#include "types.h"
#include "m2c_macros.h"

M2C_UNK GsU_00000000();                             /* static */
M2C_UNK GsU_02000000();                             /* static */
M2C_UNK GsU_02000001();                             /* static */

M2C_UNK (*func_800603DC(s32 arg0))() {
    switch (arg0) {                                 /* irregular */
    case 0x2000000:
        return GsU_02000000;
    case 0x2000001:
        return GsU_02000001;
    default:
        return GsU_00000000;
    }
}
