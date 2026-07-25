/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern u8 D_800E9EC8[];
extern void func_800158B8(void);
extern void func_80015870(void);
extern void func_80015998(void);

void func_80015B50(void)
{
    func_800158B8();
    D_800E9EC8[6] |= 2;
    func_80015870();
    func_80015998();
}
