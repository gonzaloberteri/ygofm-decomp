/* decomp-flags: opt=-O2 as_G=8 */
#include "types.h"

extern u16 D_8009B3FA;
extern u8  D_8009B3EF;

extern void func_8003F454(void);

s32 func_8003F70C(void)
{
    func_8003F454();
    if (D_8009B3FA != 0) {
        return 0;
    }
    return D_8009B3EF;
}
