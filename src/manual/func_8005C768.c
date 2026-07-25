/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

extern void func_8005CEF0(void);
extern void func_8005D378(void);
extern u8 GsU_00000000[];

void *func_8005C768(u32 arg0)
{
    if ((arg0 & 0xFFFF0000) == 0x3000000) {
        switch (arg0 & 0xFFFF) {
        case 0x2019:
            return (void *)func_8005CEF0;
        case 0x2119:
            return (void *)func_8005D378;
        }
    }
    return (void *)GsU_00000000;
}
