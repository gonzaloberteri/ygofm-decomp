#include "types.h"
#include "m2c_macros.h"

M2C_UNK func_80023FBC();                            /* static */

u8 func_80024060(void *arg0) {
    func_80023FBC();
    return M2C_FIELD(arg0, u8 *, 0x19);
}
