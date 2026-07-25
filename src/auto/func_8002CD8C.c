#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_800134B4();                            /* static */
M2C_UNK func_80035A64();                            /* static */
M2C_UNK func_80039E9C();                            /* static */
M2C_UNK func_800403F0();                            /* static */
extern s8 D_8009B0C0;
extern s8 D_8009B254;
extern s8 D_8009B39C;
extern s8 D_8009B3A2;

void func_8002CD8C(void) {
    D_8009B0C0 = 0;
    func_800403F0();
    func_80035A64();
    func_80039E9C();
    func_800134B4();
    D_8009B39C = 0x18;
    D_8009B254 = 0;
    D_8009B3A2 = 0x14;
}
