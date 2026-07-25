#include "types.h"
#include "m2c_macros.h"

s32 func_8002CCA8();                                /* static */
M2C_UNK func_8002CCE4(s32);                         /* static */

s32 func_8002CD48(s32 arg0) {
    s32 temp_v0;

    temp_v0 = func_8002CCA8();
    if (temp_v0 == 0) {
        func_8002CCE4(arg0);
    }
    return temp_v0;
}
