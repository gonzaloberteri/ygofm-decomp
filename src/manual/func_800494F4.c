/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern s32 *D_8009B458;

extern void func_80074E60(void);
extern void func_8004A6D8(void);
extern void func_80049434(void);

void func_800494F4(s32 *buf)
{
    u32 i;

    D_8009B458 = buf;
    for (i = 0; i < 0x212; i++) {
        *buf = 0;
        buf++;
    }
    func_80074E60();
    func_8004A6D8();
    func_80049434();
}
