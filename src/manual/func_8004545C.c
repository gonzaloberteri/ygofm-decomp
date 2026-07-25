/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Unk8004545C {
    u8 unk0000[0x1618];
    u8 unk1618;
} Unk8004545C;

extern Unk8004545C *D_8009B45C;
extern void (*D_8009B128)(void);
extern void D_8004544C(void);

void func_8004545C(void)
{
    D_8009B45C->unk1618 = 1;
    D_8009B128 = D_8004544C;
}
