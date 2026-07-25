/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"
typedef struct Blk800F2B20 { u8 unk_00[0x8]; s16 unk_08; s16 unk_0A; } Blk800F2B20;
extern Blk800F2B20 D_800F2B20;
extern s32 func_8005F174(void);
extern s32 func_8005F18C(void);
void func_8005A074(s32 arg0)
{
    if (func_8005F174() == 1) {
        if (func_8005F18C() == 1) {
            return;
        }
    }
    D_800F2B20.unk_0A = (arg0 < 0 ? -arg0 : arg0) << 1;
    D_800F2B20.unk_08 = 0;
}
