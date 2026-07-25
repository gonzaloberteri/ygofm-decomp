#include "types.h"
#include "m2c_macros.h"

extern void *D_8009B458;
extern void *D_8009B45C;

M2C_UNK func_80045F3C();                            /* static */
M2C_UNK func_80046A08();                            /* static */
M2C_UNK func_800495A4();                            /* static */

void func_80047050(void) {
    if (M2C_FIELD(D_8009B458, u8 *, 0x509) != 0) {
        func_800495A4();
    }
    func_80045F3C();
    if (M2C_FIELD(D_8009B45C, u16 *, 0x40) & 8) {
        func_80046A08();
    }
}
