/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Slot800F5918 {
    /* 0x0 */ void *key;
    /* 0x4 */ s32 value;
} Slot800F5918;

extern Slot800F5918 D_800F5918[];
extern s32 GsU_00000000;

s32 func_800601D0(void *key)
{
    Slot800F5918 *p = D_800F5918;
    s32 i;

    if (key == &GsU_00000000) {
        return -1;
    }
    for (i = 0; i < 0x50; i++, p++) {
        if (p->key == key) {
            return p->value;
        }
    }
    return -1;
}
