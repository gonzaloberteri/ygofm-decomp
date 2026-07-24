/* Clears a byte in the same global block as src/globals.c.  Kept separate
 * because the two functions are not adjacent in the original binary, so they
 * cannot belong to one translation unit. */

#include "types.h"

typedef struct Game {
    char _pad0[0x815];
    u8   field_815;
} Game;

extern Game *D_8009B458;

void func_800495DC(void)
{
    D_8009B458->field_815 = 0;
}
