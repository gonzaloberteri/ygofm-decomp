/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"
typedef struct Blk800F2B20 {
    u8  unk_00[0x22];
    s16 unk_22;
    u8  unk_24[0x2A - 0x24];
    s16 unk_2A;
} Blk800F2B20;
extern Blk800F2B20 D_800F2B20;
extern s32 func_8005F174(void);
extern s32 func_8005F18C(void);
void func_8005A010(s32 arg0, s32 arg1)
{
    if (func_8005F174() == 1) {
        if (func_8005F18C() == 1) {
            return;
        }
    }
    D_800F2B20.unk_22 = arg0;
    D_800F2B20.unk_2A = arg1;
}
