#ifndef TYPES_H
#define TYPES_H

typedef signed char        s8;
typedef unsigned char      u8;
typedef signed short       s16;
typedef unsigned short     u16;
typedef signed int         s32;
typedef unsigned int       u32;
typedef signed long long   s64;
typedef unsigned long long u64;
typedef float              f32;
typedef double             f64;

/* m2c emits NULL in pointer comparisons, and generated files include only this
 * header and m2c_macros.h -- not the Psy-Q headers -- so nothing else defines
 * it.  It was the single largest cause of compile failures in the automated
 * pass. */
#ifndef NULL
#define NULL 0
#endif

#endif
