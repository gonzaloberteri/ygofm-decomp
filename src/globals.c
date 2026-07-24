/* Setter reached through the global at D_8009B458.
 *
 * D_8009B458 is declared extern rather than defined here, which is why it is
 * addressed through %hi/%lo instead of $gp -- GCC only uses the small-data
 * area for variables whose definition it can see. */

#include "types.h"

typedef struct Game {
    char _pad0[0x81C];
    s32  field_81C;
} Game;

extern Game *D_8009B458;

void func_80049594(s32 value)
{
    D_8009B458->field_81C = value;
}
