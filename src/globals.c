/* Two setters reached through the global at D_8009B458.  Field offsets are
 * recovered from the store offsets in the original assembly. */

typedef unsigned char u8;
typedef signed int s32;

typedef struct Game {
    char _pad0[0x815];
    u8   field_815;
    char _pad1[0x6];
    s32  field_81C;
} Game;

extern Game *D_8009B458;

void func_80049594(s32 value)
{
    D_8009B458->field_81C = value;
}

void func_800495DC(void)
{
    D_8009B458->field_815 = 0;
}
