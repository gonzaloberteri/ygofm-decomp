#include "types.h"
#include "m2c_macros.h"

extern u8 D_8009B268;
extern s8 D_8009B269;
extern u8 D_8009B26C;
extern u8 D_8009B26D;

M2C_UNK func_8018001C(u8, u8);                      /* extern */
s32 func_80180390();                                /* extern */
M2C_UNK func_80180DD0();                            /* extern */
M2C_UNK func_800137E4();                            /* static */
M2C_UNK func_80015A00();                            /* static */
M2C_UNK func_80015B00();                            /* static */
M2C_UNK func_8002D458(s32);                         /* static */
void func_8002D588();                               /* static */
M2C_UNK func_80039E9C();                            /* static */
M2C_UNK func_8003FF34();                            /* static */
M2C_UNK func_8005B85C();                            /* static */
M2C_UNK rand();                                     /* static */

void func_8002D588(void) {
    s32 temp_v0;
    u8 temp_v1;

    temp_v1 = D_8009B26C;
    if (!(temp_v1 & 0x40)) {
        D_8009B26C = (u8) (temp_v1 | 0x40);
        func_8005B85C();
        func_800137E4();
        func_80039E9C();
        func_8018001C(D_8009B268, D_8009B26D);
        func_80015A00();
    }
    rand();
    temp_v0 = func_80180390();
    if (temp_v0 >= 0) {
        func_8003FF34();
        func_80015B00();
        func_80180DD0();
        func_8002D458(temp_v0);
        D_8009B269 = 8;
    }
}
