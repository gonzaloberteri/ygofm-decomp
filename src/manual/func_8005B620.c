/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

void func_8005B620(s32 *dst, s32 *src, s32 n)
{
    while (--n != -1) {
        *dst++ = *src++;
    }
}
