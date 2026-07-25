#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B260;

s32 func_8002C604();                                /* static */

s32 func_8002C68C(void) {
    s32 temp_v0;

    temp_v0 = func_8002C604();
    if (temp_v0 != 0) {
        D_8009B260 = (u8) (D_8009B260 | 0x80);
    }
    return temp_v0;
}
