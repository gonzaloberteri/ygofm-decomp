/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

typedef struct DispPacket {
    u32 tag;
    u8  unk04;
    u8  unk05;
    u8  unk06;
    u8  unk07;
    u32 unk08;
    u32 unk0C;
    u32 unk10;
    u32 unk14;
} DispPacket;

extern DispPacket D_800E9EC8;

extern void func_80015780(void);
extern void func_8001572C(void);

void func_80015C48(void)
{
    func_80015780();
    D_800E9EC8.unk06 |= 6;
    func_8001572C();
}
