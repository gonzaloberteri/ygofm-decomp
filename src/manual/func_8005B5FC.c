/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"

void func_8005B5FC(u32 *dst, u32 value, u32 count)
{
    while (count-- != 0) {
        *dst++ = value;
    }
}
