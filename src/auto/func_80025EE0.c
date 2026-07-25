#include "types.h"
#include "m2c_macros.h"

extern s16 D_8009B220;

s32 func_80024E24();                                /* static */
void func_80025EE0();                               /* static */
void *func_8002C68C(M2C_UNK);                       /* static */
M2C_UNK func_8003FEE0(M2C_UNK);                     /* static */

void func_80025EE0(void) {
    void *temp_v0;

    if (func_80024E24() == 0) {
        temp_v0 = func_8002C68C(0x12);
        M2C_FIELD(temp_v0, s16 *, 0) = 0xA0;
        M2C_FIELD(temp_v0, s16 *, 2) = 0x78;
        M2C_FIELD(temp_v0, s16 *, 0x1A) = 1;
        func_8003FEE0(2);
        return;
    }
    D_8009B220 = 0;
}
