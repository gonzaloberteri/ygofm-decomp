/* decomp-flags: opt=-O1 as_G=8 */
#include "types.h"

typedef struct Unk8004703C {
    u8  unk00[0x40];
    s16 unk40;
} Unk8004703C;

extern Unk8004703C *D_8009B45C;

s32 func_8004703C(void)
{
    return D_8009B45C->unk40;
}
