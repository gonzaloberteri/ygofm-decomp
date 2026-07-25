/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"
typedef struct SndWork { u8 unk_000[0x81C]; s32 unk_81C; } SndWork;
extern SndWork *D_8009B458;
extern void func_8004A6D8(void);
extern void func_8004B910(void);
extern void func_80049434(void);
void func_80049640(void)
{
    s32 n;
    func_8004A6D8();
    n = D_8009B458->unk_81C;
    if (n > 0) {
        if (n < 4) {
            func_8004B910();
        }
    }
    func_80049434();
}
