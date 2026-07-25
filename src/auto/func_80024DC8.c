#include "types.h"
#include "m2c_macros.h"

extern s8 D_8009B26C;
extern s8 D_8009B360;
extern s8 D_8009B361;
extern s8 D_8009B364;
extern s8 D_8009B369;
extern s16 D_8009B36A;
extern s16 D_8009B370;
extern s16 D_8009B372;
extern s16 D_8009B374;

void func_80024DC8(s8 arg0, s8 arg1, s16 arg2, s16 arg3) {
    D_8009B36A = 0x7270;
    D_8009B374 = 0x7280;
    D_8009B360 = arg0;
    D_8009B361 = arg1;
    D_8009B370 = arg2;
    D_8009B372 = arg3;
    D_8009B364 = 0;
    D_8009B369 = 0;
    D_8009B26C = 3;
}
