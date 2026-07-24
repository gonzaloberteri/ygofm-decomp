/* Sets a mode byte and clears bit 4 of a halfword flags field. */

typedef unsigned char u8;
typedef unsigned short u16;

typedef struct Entity {
    char _pad0[0x8];
    u16  flags;      /* 0x08 */
    char _pad1[0x5F];
    u8   mode;       /* 0x69 */
} Entity;

void func_80040410(Entity *e, u8 mode)
{
    e->mode = mode;
    e->flags &= ~0x10;
}
