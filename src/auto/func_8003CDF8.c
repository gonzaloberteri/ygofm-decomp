#include "types.h"
#include "m2c_macros.h"

extern u16 D_8009B394;
extern u16 D_8009B396;
extern u16 D_8009B398;
extern u16 D_8009B39A;
extern u16 D_8009B39E;
extern u16 D_8009B3A0;
extern u16 D_8009B3A4;
extern u16 D_8009B3A6;
extern u16 D_8009B3AC;

void func_8003CDF8(void) {
    D_8009B3AC = (u16) D_8009B3A4;
    D_8009B3A0 = (u16) D_8009B398;
    D_8009B39E = (u16) D_8009B394;
    D_8009B3A4 = (u16) D_8009B3A6;
    D_8009B398 = (u16) D_8009B39A;
    D_8009B394 = (u16) D_8009B396;
}
