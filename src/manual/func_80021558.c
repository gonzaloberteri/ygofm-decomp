/* decomp-flags: opt=-O1 as_G=0 */
#include "types.h"

typedef struct Threshold {
    /* 0x0 */ s16 limit;
    /* 0x2 */ s16 value;
} Threshold;

extern Threshold D_801798A8[][5];

s16 func_80021558(s32 row, s32 value)
{
    Threshold *p = D_801798A8[row];

    for (;;) {
        if (value < p->limit) {
            return p->value;
        }
        p++;
    }
}
