/* First decompiled translation unit.
 *
 * func_8006C2FC writes three consecutive bytes from its 2nd/3rd/4th arguments
 * -- the classic setRGB0 shape used all over Psy-Q primitive setup code. */

typedef unsigned char u8;

void func_8006C2FC(u8 *p, u8 r, u8 g, u8 b)
{
    p[0] = r;
    p[1] = g;
    p[2] = b;
}
