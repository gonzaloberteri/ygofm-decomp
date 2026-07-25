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

extern void func_800158B8(void);
extern void func_80015870(void);

void func_80015C84(void)
{
    func_800158B8();
    D_800E9EC8.unk06 |= 2;
    func_80015870();
}
