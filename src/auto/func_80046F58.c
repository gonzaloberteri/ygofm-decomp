#include "types.h"
#include "m2c_macros.h"

M2C_UNK SpuQuit();                                  /* static */
M2C_UNK SpuSetIRQ(M2C_UNK);                         /* static */
M2C_UNK func_8004763C();                            /* static */
M2C_UNK func_80047EC4();                            /* static */
M2C_UNK func_800492D8();                            /* static */
M2C_UNK func_80049640();                            /* static */

void func_80046F58(void) {
    func_80047EC4();
    func_8004763C();
    func_800492D8();
    func_80049640();
    SpuSetIRQ(0);
    SpuQuit();
}
