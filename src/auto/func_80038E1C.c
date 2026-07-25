#include "types.h"
#include "m2c_macros.h"

extern M2C_UNK (*D_8009B340)(void *);
extern s32 D_8009B350;

s32 func_80037C74();                                /* static */
void func_80038E1C(void *arg0);                     /* static */

void func_80038E1C(void *arg0) {
    M2C_UNK (*temp_v1)(void *);

    M2C_FIELD(arg0, s16 *, 0x38) = 0x1000;
    M2C_FIELD(arg0, u8 *, 0x56) = (u8) (M2C_FIELD(arg0, u8 *, 0x56) + 1);
    if (func_80037C74() != 0) {
        M2C_FIELD(arg0, s8 *, 0x51) = 4;
    }
    temp_v1 = D_8009B340;
    D_8009B350 = 1;
    if (temp_v1 != NULL) {
        temp_v1(arg0);
    }
}
