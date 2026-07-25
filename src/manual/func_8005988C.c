/* decomp-flags: opt=-O2 as_G=0 */
#include "types.h"
extern s32 PCopen(char *, f32, f32);
extern s32 PClseek(s32, s32, s32);
extern s32 func_80073724(s32);

s32 func_8005988C(char *name)
{
    s32 fd;
    s32 len;

    fd = PCopen(name, 0.0f, 0.0f);
    if (fd < 0) {
        return -1;
    }
    len = PClseek(fd, 0, 2);
    func_80073724(fd);
    return len;
}
