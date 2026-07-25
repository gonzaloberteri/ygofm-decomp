/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern u8 D_8009B0C0;
extern u8 D_8009B254;
extern u8 D_8009B39C;
extern u8 D_8009B3A2;

extern void func_800403F0(void);
extern void func_80035A64(void);
extern void func_80039E9C(void);
extern void func_800134B4(void);

void func_8002CD8C(void)
{
    D_8009B0C0 = 0;
    func_800403F0();
    func_80035A64();
    func_80039E9C();
    func_800134B4();
    D_8009B39C = 0x18;
    D_8009B254 = 0;
    D_8009B3A2 = 0x14;
}
