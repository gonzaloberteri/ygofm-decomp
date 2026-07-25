#include "types.h"
#include "m2c_macros.h"

extern u16 D_8009B394;
extern u16 D_8009B398;
extern u16 D_8009B39E;
extern u16 D_8009B3A0;
extern u16 D_8009B3A4;
extern u16 D_8009B3AC;

void func_8003CE48(void) {
    D_8009B3A4 = (u16) D_8009B3AC;
    D_8009B398 = (u16) D_8009B3A0;
    D_8009B394 = (u16) D_8009B39E;
}
