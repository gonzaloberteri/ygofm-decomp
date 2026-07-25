#ifndef GAME_H
#define GAME_H

/* ===========================================================================
 * game.h -- recovered data structures and globals for
 *           Yu-Gi-Oh! Forbidden Memories (SLUS-01411)
 *
 * ---------------------------------------------------------------------------
 * HOW MUCH TO TRUST THIS FILE
 * ---------------------------------------------------------------------------
 * Everything here was derived from the 161 functions in `src/manual/` and
 * `src/auto/` that already **byte-match** the original executable, plus
 * corroboration read out of `asm/code_002800.s`.  Every struct records the
 * files it came from, so any claim can be re-checked.
 *
 * A field offset that a byte-matching file *accesses* is verified: if the
 * offset were wrong the load/store displacement would differ and the function
 * would not have matched.  That is the strongest evidence this project has.
 *
 * A field offset that a byte-matching file only *pads over* is NOT evidence.
 * The decompiled files are full of declarations like
 *
 *     u8 unk0000[0x512];  s16 unk0512;
 *
 * where only `unk0512` is real; the array in front of it exists solely to
 * place it.  Padding was chosen by whoever wrote the file and carries no
 * information.  This header therefore only names fields that are actually
 * read or written somewhere, and leaves everything else as `pad_`.
 *
 * Sizes are only stated where something establishes them (an index multiply, a
 * clear loop, a `p++`).  Where a size is unknown it says so.
 *
 * Finally: byte-equality proves the bytes, not the understanding.  PLAN.md
 * records three occasions where a confident structural claim survived the
 * SHA-1 gate and was still wrong.  Treat the *offsets* as facts and the
 * *comments* as the best current reading.
 *
 * ---------------------------------------------------------------------------
 * OFFSET CONVENTION
 * ---------------------------------------------------------------------------
 * Every member carries its byte offset in a leading comment:
 *
 *     /_* 0x04 *_/ s16 unk_04;
 *
 * Gaps are explicit `char pad_NN[len];` members, also offset-tagged.  The
 * compiler is GCC 2.95.2, which has no `_Static_assert`, so struct sizes
 * cannot be checked mechanically -- they are asserted in a trailing comment
 * (`/_* size 0x28 *_/`) and must be checked by eye against the offsets.
 *
 * Pads are `char` so they never impose alignment of their own; each following
 * member lands on its natural alignment because the real object is naturally
 * aligned.  Where a struct's total size is known, an explicit trailing pad
 * carries it out to that size.
 *
 * ---------------------------------------------------------------------------
 * $gp AND THE D_8009xxxx SYMBOL NAMES  --  READ THIS, IT IS CONFUSING
 * ---------------------------------------------------------------------------
 * The startup code at 0x80012A54 loads
 *
 *     lui   $gp, 0x800A
 *     addiu $gp, $gp, -0x50F8      ->   $gp = 0x8009AF08
 *
 * so a disassembly line `lw $v0, 0x554($gp)` and the symbol
 * `D_8009B45C` (= 0x8009AF08 + 0x554) name **the same object**.  Roughly
 * 46% of game functions address their globals this way, because the recovered
 * build used `-G8` (small objects go in the small-data area).  Each global
 * below is tagged with both forms.
 *
 * The trap: `gp + N` and `<some struct pointer> + N` are different things that
 * look identical in the disassembly.  Two live examples:
 *
 *   - `0x4C0($gp)` is D_8009B3C8, a small-data global.
 *     `0x4C0(sound work area)` is the SpuVoiceAttr block inside SoundWork.
 *     Same displacement, unrelated objects.
 *   - `0x554($gp)` *holds a pointer*; `0x514(that pointer)` is a GameState
 *     field, while `0x514($gp)` would be D_8009B41C.  PLAN.md's note about
 *     "u16 master volumes at +0x514/+0x516" is an offset inside the
 *     **SoundWork** block reached through D_8009B458, not a $gp offset.
 *
 * ---------------------------------------------------------------------------
 * HAZARD: INCLUDING THIS HEADER CAN BREAK A MATCHING FUNCTION
 * ---------------------------------------------------------------------------
 * This is not a normal header.  Per PLAN.md, `-G8` puts an object in the
 * small-data area based on **the size in your declaration**, not the size of
 * the real object: cc1 emits `.extern sym, size` and gas honours it.  So
 *
 *     extern u8  D_8009B145;        ->  sb $v0, 0x23D($gp)
 *     extern u8  D_8009B145[16];    ->  %hi/%lo pair (different instructions)
 *
 * Several already-matching files depend on their *local* declaration being
 * exactly the width it is -- including a shared, differently-sized declaration
 * would change the emitted instructions and lose the match.  The same applies
 * to `volatile`, which changes instruction *count*.
 *
 * Therefore: do not retrofit existing matched files onto this header.  When
 * using it for new work, if a function stops matching, suspect the declaration
 * width or `volatile` before suspecting the C.
 * ===========================================================================
 */

#include "types.h"

/* $gp as set by the startup code at 0x80012A54.  `gp + N` == `D_<0x8009AF08+N>`. */
#define GP_BASE 0x8009AF08

/* Absolute addresses established from the disassembly (see the notes on
 * GameState and SoundWork below).  These are compile-time facts about the
 * original build, recorded so a reader can convert between an offset in the
 * disassembly and an offset in a struct. */
#define GAME_STATE_ADDR  0x801E0000  /* value stored to gp+0x554 at 0x80046788 */
#define SOUND_WORK_ADDR  0x801E1670  /* argument to func_800494F4 at 0x800468E8 */


/* ===========================================================================
 * SECTION 1 -- GameState: the block behind D_8009B45C  (gp + 0x554)
 * ===========================================================================
 * D_8009B45C is a *pointer variable* at gp+0x554.  func_80046768 sets it:
 *
 *     0x80046788   sw  $v0, 0x554($gp)        with $v0 = 0x801E0000
 *     0x8004678C   sw  $v1, 0x558($gp)        with $v1 = 0x801E1650
 *     0x80046790   zero loop, 0x801E0000 .. 0x801EA7FF inclusive
 *
 * so the target is the fixed address 0x801E0000, not a heap allocation, and
 * 0x801E0000..0x801EA800 is cleared at init.  The neighbouring pointer at
 * gp+0x558 (D_8009B460) is 0x801E1650 == GameState + 0x1650, and the highest
 * field ever touched through D_8009B45C is 0x164B -- so **GameState is
 * 0x1650 bytes** and gp+0x558 points at whatever follows it.  (The 0xA800
 * clear covers several later blocks too, including SoundWork.)
 *
 * Derived from:
 *   src/manual/func_80044D48.c   0x0512, 0x053C, 0x073C, 0x093C, 0x0B3C,
 *                                0x153C, 0x1540, 0x1544, 0x1548
 *   src/manual/func_80044DA0.c   0x0514, 0x0515
 *   src/manual/func_80046990.c   0x003C, 0x0040, 0x004A
 *   src/manual/func_8004703C.c   0x0040
 *   src/manual/func_80047314.c   0x164B
 *   src/manual/func_800490F0.c   0x1582, 0x1584
 *   src/manual/func_80049108.c   0x1582, 0x1584
 *   src/manual/func_8004545C.c   0x1618
 *   src/auto/func_80049120.c     0x1582
 *   src/auto/func_80049200.c     0x164B
 *   asm/code_002800.s            everything else, by tracking the register
 *                                loaded from 0x554($gp)
 *
 * Only offsets that some instruction actually addresses are named.  The map is
 * sparse: this struct is the union of many subsystems' state and most of it has
 * never been touched by decompiled code.
 */
typedef struct GameState {
    /* 0x0000 */ u16  unk_0000;      /* also written by swl/swr as part of a 4-byte
                                      * unaligned copy spanning 0x0000..0x0007 */
    /* 0x0002 */ u16  unk_0002;
    /* 0x0004 */ u16  unk_0004;
    /* 0x0006 */ char pad_0006[0x36];
    /* 0x003C */ s32  unk_003C;      /* cleared by func_80046990 */
    /* 0x0040 */ u16  unk_0040;      /* bitfield.  func_80046990 sets bits 0x0A;
                                      * elsewhere bit 0x04 is cleared.  Returned
                                      * as a signed s16 by func_8004703C. */
    /* 0x0042 */ u16  unk_0042;
    /* 0x0044 */ u16  unk_0044;
    /* 0x0046 */ char pad_0046[0x02];
    /* 0x0048 */ u8   unk_0048;
    /* 0x0049 */ u8   unk_0049;
    /* 0x004A */ u8   unk_004A;      /* bitfield.  func_80046990 clears bits 0, 1
                                      * and 6 independently; func_80046768 sets it
                                      * to 3 then ORs 0xF0. */
    /* 0x004B */ char pad_004B[0x01];
    /* 0x004C */ s16  unk_004C;      /* read signed (lh) far more often than not */
    /* 0x004E */ u16  unk_004E;
    /* 0x0050 */ s32  unk_0050;
    /* 0x0054 */ s32  unk_0054;
    /* 0x0058 */ s32  unk_0058;
    /* 0x005C */ s32  unk_005C;
    /* 0x0060 */ s32  unk_0060;
    /* 0x0064 */ s32  unk_0064;
    /* 0x0068 */ s32  unk_0068;
    /* 0x006C */ s32  unk_006C;
    /* 0x0070 */ s32  unk_0070;
    /* 0x0074 */ s32  unk_0074;
    /* 0x0078 */ s32  unk_0078;
    /* 0x007C */ u8   unk_007C;      /* 0x007C..0x007E written as three separate
                                      * bytes, like an RGB triple */
    /* 0x007D */ u8   unk_007D;
    /* 0x007E */ u8   unk_007E;
    /* 0x007F */ char pad_007F[0x305];
    /* 0x0384 */ s32  unk_0384;      /* 0x0384..0x03CF is a dense block of s32 and
                                      * s16 written together by one initialiser --
                                      * shape unknown, listed only as a pad below */
    /* 0x0388 */ char pad_0388[0xAC]; /* 0x0388..0x0433: s32 at 0x0388, 0x03A8,
                                       * 0x03AC, 0x03B0, 0x03C4, 0x03C8;
                                       * s16 at 0x038C, 0x038E, 0x0390, 0x0392,
                                       * 0x0394, 0x0396, 0x0398, 0x039A, 0x039C,
                                       * 0x03B4, 0x03B6, 0x03B8, 0x03BA, 0x03BC,
                                       * 0x03CC, 0x03CE */
    /* 0x0434 */ u8   unk_0434;
    /* 0x0435 */ u8   unk_0435;
    /* 0x0436 */ char pad_0436[0x02];
    /* 0x0438 */ s32  unk_0438;
    /* 0x043C */ s32  unk_043C;      /* read 10x, written once -- looks like a
                                      * pointer or handle */
    /* 0x0440 */ u16  unk_0440;
    /* 0x0442 */ u16  unk_0442;
    /* 0x0444 */ s32  unk_0444;
    /* 0x0448 */ s32  unk_0448;
    /* 0x044C */ u16  unk_044C[0x40];/* func_80048658 indexes it with
                                      * (id & 0x1F) + ((id & 0x100) != 0) * 32
                                      * and treats 0xFFFF as "no entry", so it is
                                      * 64 u16 slots, not opaque padding. */
    /* 0x04CC */ s32  unk_04CC;      /* read once only */
    /* 0x04D0 */ char pad_04D0[0x40];
    /* 0x0510 */ s16  unk_0510;
    /* 0x0512 */ s16  unk_0512;      /* zeroed by func_80044D48; also set to -0x40 */
    /* 0x0514 */ u8   unk_0514;      /* func_80044DA0 sets 0x0514 and 0x0515 to
                                      * 0x80 together */
    /* 0x0515 */ u8   unk_0515;
    /* 0x0516 */ char pad_0516[0x02];
    /* 0x0518 */ s32  unk_0518;
    /* 0x051C */ s32  unk_051C;
    /* 0x0520 */ s32  unk_0520;
    /* 0x0524 */ char pad_0524[0x04];
    /* 0x0528 */ s32  unk_0528;
    /* 0x052C */ s32  unk_052C;
    /* 0x0530 */ u8   unk_0530;
    /* 0x0531 */ u8   unk_0531;
    /* 0x0532 */ u8   unk_0532;
    /* 0x0533 */ u8   unk_0533;
    /* 0x0534 */ s16  unk_0534;
    /* 0x0536 */ char pad_0536[0x02];
    /* 0x0538 */ s32  unk_0538;
    /* 0x053C */ u8   buf_053C[0x200];  /* four buffers, 0x200/0x200/0x200/0xA00.
                                         * func_80044D48 publishes their addresses
                                         * into the four pointers at 0x153C. */
    /* 0x073C */ u8   buf_073C[0x200];
    /* 0x093C */ u8   buf_093C[0x200];
    /* 0x0B3C */ u8   buf_0B3C[0xA00];
    /* 0x153C */ u8  *ptr_153C;      /* = &buf_053C, set by func_80044D48 */
    /* 0x1540 */ u8  *ptr_1540;      /* = &buf_073C */
    /* 0x1544 */ u8  *ptr_1544;      /* = &buf_093C */
    /* 0x1548 */ u8  *ptr_1548;      /* = &buf_0B3C */
    /* 0x154C */ s32  unk_154C;      /* 0x154E is also read as an s16 -- i.e. the
                                      * high half of this word is read on its own */
    /* 0x1550 */ s32  unk_1550;      /* same: 0x1552 read as s16 */
    /* 0x1554 */ char pad_1554[0x0C];
    /* 0x1560 */ s32  unk_1560;
    /* 0x1564 */ s32  unk_1564;      /* read 13x -- pointer or handle */
    /* 0x1568 */ char pad_1568[0x10];
    /* 0x1578 */ s16  unk_1578;
    /* 0x157A */ s16  unk_157A;
    /* 0x157C */ s16  unk_157C;
    /* 0x157E */ s16  unk_157E;
    /* 0x1580 */ s16  unk_1580;
    /* 0x1582 */ s16  unk_1582;      /* func_800490F0/func_80049108 write 0x1582 and
                                      * 0x1584 as a pair; func_80049120 returns
                                      * (unk_1582 != 0) */
    /* 0x1584 */ u8   unk_1584;      /* declared s8 in func_800490F0.c, u8 in
                                      * src/auto -- store-only there, so the
                                      * signedness is not pinned */
    /* 0x1585 */ char pad_1585[0x01];
    /* 0x1586 */ s16  unk_1586;
    /* 0x1588 */ s16  unk_1588;
    /* 0x158A */ u8   unk_158A;
    /* 0x158B */ char pad_158B[0x61];
    /* 0x15EC */ u8   unk_15EC;      /* 0x15EC..0x15EF read as four separate bytes */
    /* 0x15ED */ u8   unk_15ED;
    /* 0x15EE */ u8   unk_15EE;
    /* 0x15EF */ u8   unk_15EF;
    /* 0x15F0 */ char pad_15F0[0x28];
    /* 0x1618 */ u8   unk_1618;      /* set to 1 by func_8004545C */
    /* 0x1619 */ u8   rec_1619[0x30]; /* 0x1619..0x1642: three 0x10-byte records,
                                       * 0x1619 / 0x1629 / 0x1639, each copied from
                                       * rodata by func_80046768 with unaligned
                                       * swl/swr pairs plus 3 trailing sb.  The
                                       * unaligned start address is why this is a
                                       * byte array and not a struct. */
    /* 0x1649 */ u8   unk_1649;
    /* 0x164A */ u8   unk_164A;
    /* 0x164B */ u8   unk_164B;      /* passed as the 2nd arg of func_8004733C by
                                      * func_80047314 */
    /* 0x164C */ char pad_164C[0x04];
} GameState;                          /* size 0x1650 */


/* ===========================================================================
 * SECTION 2 -- SoundWork: the block behind D_8009B458  (gp + 0x550)
 * ===========================================================================
 * D_8009B458 is a *pointer variable* at gp+0x550, set by func_800494F4, which
 * also zeroes 0x212 words == **0x848 bytes** starting at the buffer -- so that
 * is the size of the block.  The highest offset any instruction touches is
 * 0x845, which corroborates it.  func_80046768 calls func_800494F4 with
 * 0x801E1670 (asm 0x800468E8), i.e. immediately after GameState.
 *
 * Layout, in the order the evidence establishes it:
 *
 *   0x000  SoundChannel[16]   stride 0x18 proved by func_8004B6E8:
 *                             (n*2 + n) << 3 == n * 24.  The count of 16 comes
 *                             from PLAN.md and is *not* independently confirmed
 *                             here; 16 * 0x18 == 0x180 exactly reaches the next
 *                             known object, which is consistent.
 *   0x180  SoundVoice[20]     stride 0x28 proved by func_80049CF8/func_80049DD8
 *                             (`addiu $s1, $s1, 0x28` walking 0x183/0x18D/
 *                             0x194/0x196).  The bound is the s16 at 0x510, and
 *                             func_80049600 rejects any value >= 0x15, so the
 *                             maximum is 20.  0x180 + 20*0x28 == 0x4A0, and the
 *                             next field used is 0x4A4 -- the array fits exactly.
 *   0x4A4  transfer request   see SoundXfer below
 *   0x4C0  SpuVoiceAttr       proved at asm 0x8004A2C8:
 *                             `sw $a0, 0x4C0($v1); addiu $a0, $v1, 0x4C0`
 *                             then `jal SpuSetVoiceAttr` (0x8004A2E0).  The
 *                             first word is therefore SpuVoiceAttr.voice.
 *
 * Derived from:
 *   src/manual/func_800494F4.c   the 0x848 clear, and the pointer store
 *   src/manual/func_8004B6E8.c   channel stride 0x18
 *   src/manual/func_80049600.c   0x0510
 *   src/manual/func_8004BAE4.c   0x07DC, 0x07EC
 *   src/globals.c                0x081C
 *   src/globals2.c               0x0815
 *   src/auto/func_80049594.c     0x081C
 *   src/auto/func_800495DC.c     0x0815
 *   src/auto/func_800495EC.c     0x0815
 *   src/auto/func_8004975C.c     0x04A4 and the SoundXfer sub-fields
 *   asm/code_002800.s            everything else
 */

/* 0x18-byte record, 16 of them at SoundWork+0x000.
 * Only offset 0x00 is established (func_8004B6E8 stores a byte there). */
typedef struct SoundChannel {
    /* 0x00 */ u8   unk_00;         /* func_8004B6E8(index, value) writes this */
    /* 0x01 */ char pad_01[0x03];
    /* 0x04 */ u8   unk_04;         /* func_8004B374 clears it when a note on
                                     * this channel is released */
    /* 0x05 */ char pad_05[0x02];
    /* 0x07 */ u8   unk_07;         /* func_8004A43C compares it against the
                                     * request's unk_1A and feeds it to
                                     * func_8004A3BC -- a note or key number */
    /* 0x08 */ char pad_08[0x10];
} SoundChannel;                      /* size 0x18 */

/* 0x28-byte record, 20 of them at SoundWork+0x180. */
typedef struct SoundVoice {
    /* 0x00 */ char pad_00[0x03];
    /* 0x03 */ u8   unk_03;         /* tested as `>> 4`, so the high nibble is a
                                     * separate field from the low nibble */
    /* 0x04 */ char pad_04[0x01];
    /* 0x05 */ u8   unk_05;         /* func_8004B374 matches on unk_03 and this
                                     * together when releasing a note */
    /* 0x06 */ char pad_06[0x07];
    /* 0x0D */ u8   unk_0D;         /* must be non-zero for the voice to be
                                     * pushed to the SPU */
    /* 0x0E */ char pad_0E[0x06];
    /* 0x14 */ u16  unk_14;         /* copied into SpuVoiceAttr+0x18 (note) */
    /* 0x16 */ u16  unk_16;         /* copied into SpuVoiceAttr+0x1A (sample_note) */
    /* 0x18 */ char pad_18[0x06];
    /* 0x1E */ u16  unk_1E;         /* a countdown: func_8004C84C decrements it
                                     * once per call while unk_03 < 0x10, and
                                     * clamps it to 0 otherwise.  Read and
                                     * written as a halfword. */
    /* 0x20 */ char pad_20[0x08];
} SoundVoice;                        /* size 0x28 */

/* The 0x4A4 sub-block, reached as `base + 0x4A4` and then indexed.
 * From src/auto/func_8004975C.c and asm 0x800497E0.  Size 0x1C rather than a
 * round 0x20 because the SpuVoiceAttr block starts at 0x4C0 == 0x4A4 + 0x1C. */
typedef struct SoundXfer {
    /* 0x00 */ s16  unk_00;         /* compared for equality against a caller's
                                     * s16 before the transfer is allowed --
                                     * an id or generation counter */
    /* 0x02 */ char pad_02[0x02];
    /* 0x04 */ s32  unk_04;
    /* 0x08 */ char pad_08[0x04];
    /* 0x0C */ s32  unk_0C;         /* written with the source address after a
                                     * successful transfer */
    /* 0x10 */ s32  unk_10;         /* byte count passed to func_80077150 */
    /* 0x14 */ u32  unk_14;         /* passed to SpuSetTransferStartAddr -- an
                                     * SPU-local address */
    /* 0x18 */ u8   unk_18;         /* 0x18..0x1B (== 0x4BC..0x4BF absolute) are
                                     * read and written as four separate bytes */
    /* 0x19 */ u8   unk_19;
    /* 0x1A */ u8   unk_1A;
    /* 0x1B */ u8   unk_1B;
} SoundXfer;                         /* size 0x1C */

typedef struct SoundWork {
    /* 0x000 */ SoundChannel channels[16];   /* 16 * 0x18 == 0x180 */
    /* 0x180 */ SoundVoice   voices[20];     /* 20 * 0x28 == 0x320, ends 0x4A0 */
    /* 0x4A0 */ char pad_4A0[0x04];
    /* 0x4A4 */ SoundXfer    xfer;           /* 0x4A4..0x4BF */
    /* 0x4C0 */ u8   spu_attr[0x40];
    /* spu_attr is the SpuVoiceAttr passed to SpuSetVoiceAttr.  Proved at
     * asm 0x8004A2C8: `sw $a0, 0x4C0($v1); addiu $a0, $v1, 0x4C0` immediately
     * before `jal SpuSetVoiceAttr`, so +0x00 is SpuVoiceAttr.voice.  Kept as a
     * byte array because the project does not vendor the Psy-Q libspu headers.
     * Observed accesses line up with SpuVoiceAttr exactly:
     *   +0x00 voice (sw)   +0x04 mask (sw)      +0x08 mode (sh)
     *   +0x0A volume.left  +0x0C volume.right   +0x0E volmode.left
     *   +0x1C envx         +0x24 loop_addr      +0x3A rr   +0x3C sl
     * Declared 0x40 bytes, not the 0x44 of the full SpuVoiceAttr, because
     * SoundWork+0x500 (== attr+0x40, i.e. `adsr2`) is written 22 times as a
     * *single byte* with flag-like values, which is not how adsr2 would ever be
     * used.  Either the game's attr struct stops at `sl` or 0x500 genuinely
     * overlaps it.  UNRESOLVED -- flagged rather than guessed. */
    /* 0x500 */ u8   unk_500;      /* set 22 times, read once: 0 and 1 -- reads
                                    * like a "sound driver busy/enabled" flag */
    /* 0x501 */ u8   unk_501;
    /* 0x502 */ u8   unk_502;
    /* 0x503 */ u8   unk_503;
    /* 0x504 */ s32  unk_504;
    /* 0x508 */ u8   unk_508;
    /* 0x509 */ u8   unk_509;
    /* 0x50A */ char pad_50A[0x02];
    /* 0x50C */ void (*unk_50C)(void);
                                   /* a callback, not an integer: func_8004B734
                                    * loads it and does `jalr $v0` when non-null.
                                    * Same width as the s32 it replaces. */
    /* 0x510 */ s16  unk_510;      /* voice count.  Read signed 26 times as the
                                    * `i < unk_510` bound of the voices[] loops;
                                    * func_80049600 refuses to set it to 0 or to
                                    * anything >= 0x15. */
    /* 0x512 */ u16  unk_512;      /* purpose unknown */
    /* 0x514 */ u16  unk_514;      /* PLAN.md calls 0x514/0x516 "u16 master
                                    * volumes".  Confirmed only as far as: two
                                    * adjacent u16s written together and read
                                    * together.  The volume reading is plausible
                                    * (a left/right pair) but unproven here. */
    /* 0x516 */ u16  unk_516;
    /* 0x518 */ char pad_518[0x24];
    /* 0x53C */ u8   unk_53C;
    /* 0x53D */ char pad_53D[0x29F];
    /* 0x7DC */ u8  *unk_7DC;      /* byte-stream base.  func_8004BAE4 reads
                                    * unk_7DC[pos] and bounds pos against
                                    * unk_7EC -- a sequence/script reader. */
    /* 0x7E0 */ s16  unk_7E0;
    /* 0x7E2 */ s16  unk_7E2;
    /* 0x7E4 */ s16  unk_7E4;
    /* 0x7E6 */ s16  unk_7E6;
    /* 0x7E8 */ s32  unk_7E8;
    /* 0x7EC */ u32  unk_7EC;      /* length of the unk_7DC stream; compared
                                    * unsigned against the read position */
    /* 0x7F0 */ s32  unk_7F0;
    /* 0x7F4 */ s32  unk_7F4;
    /* 0x7F8 */ u16  unk_7F8;
    /* 0x7FA */ u16  unk_7FA;
    /* 0x7FC */ u16  unk_7FC;
    /* 0x7FE */ char pad_7FE[0x03];
    /* 0x801 */ u8   unk_801;
    /* 0x802 */ char pad_802[0x02];
    /* 0x804 */ s32  unk_804;
    /* 0x808 */ s32  unk_808;
    /* 0x80C */ s32  unk_80C;
    /* 0x810 */ s32  unk_810;
    /* 0x814 */ u8   unk_814;
    /* 0x815 */ u8   unk_815;      /* func_800495DC clears it, func_800495EC sets
                                    * it to 1 -- a boolean */
    /* 0x816 */ char pad_816[0x02];
    /* 0x818 */ s32  unk_818;      /* added to xfer.unk_14 before
                                    * SpuSetTransferStartAddr, and subtracted from
                                    * xfer.unk_10 -- an SPU heap base */
    /* 0x81C */ s32  unk_81C;      /* set by func_80049594 */
    /* 0x820 */ char pad_820[0x24];
    /* 0x844 */ u8   unk_844;
    /* 0x845 */ u8   unk_845;      /* highest offset used anywhere */
    /* 0x846 */ char pad_846[0x02];
} SoundWork;                        /* size 0x848 */


/* ===========================================================================
 * SECTION 3 -- the object / actor pool at D_800EFE48
 * ===========================================================================
 * 0x60 records of 0x70 bytes.  Established by:
 *   - src/manual/func_8004006C.c walks `p++` over a 0x70-byte struct for
 *     i in [0, 0x60) looking for `!(unk_08 & 0x80)`;
 *   - src/manual/func_8004002C.c does the same for i in [0x10, 0x60) but
 *     starting from the symbol D_800F0548, and
 *     0x800F0548 - 0x800EFE48 == 0x700 == 0x10 * 0x70.
 *     So **D_800F0548 is not a separate array; it is &D_800EFE48[0x10]**, and
 *     the two functions are "allocate from anywhere" vs "allocate from index
 *     0x10 up".  Both byte-match, which is what makes this solid.
 *
 * The same layout shows up as the anonymous `arg0` of a cluster of functions in
 * 0x80040000..0x80043200, all of whose offsets fall inside 0x70 and whose
 * 0x08 field is the same u16 bitfield.  That identification is *inferred*, not
 * proven -- no byte-matching function both indexes the array and takes the
 * pointer.
 *
 * The three-axis reading of 0x30/0x32/0x34 is the one piece of real semantics
 * here, and four independent byte-matching files agree on it:
 *
 *   func_80042A00:  pos = (unk_30 << 8) | unk_62;  pos += unk_36;
 *                   unk_62 = pos;  unk_30 = pos >> 8;
 *   func_80042A28:  same with 0x32 / 0x63 / 0x38
 *   func_80042A50:  same with 0x34 / 0x64 / 0x3A
 *   func_800429D8:  zeroes 0x36/0x38/0x3A and sets 0x62/0x63/0x64 to 0x80
 *
 * i.e. three 8.8 fixed-point coordinates (integer part s16, fraction u8) each
 * advanced by its own s16 delta, with the fractions reset to mid-scale.  That
 * is a position/velocity triple, and the fields are named accordingly.
 *
 * Derived from:
 *   src/manual/func_8004002C.c   0x08, array bounds
 *   src/manual/func_8004006C.c   0x08, array bounds
 *   src/manual/func_800429D8.c   0x36, 0x38, 0x3A, 0x62, 0x63, 0x64
 *   src/manual/func_80042A00.c   0x30, 0x36, 0x62
 *   src/manual/func_80042A28.c   0x32, 0x38, 0x63
 *   src/manual/func_80042A50.c   0x34, 0x3A, 0x64
 *   src/auto/func_80040410.c     0x08, 0x69   (also src/entity.c)
 *   src/auto/func_80042918.c     0x14, 0x16, 0x17
 *   src/auto/func_8004293C.c     0x14, 0x16, 0x17
 *   src/auto/func_80043178.c     0x30, 0x32, 0x36, 0x38
 *   src/auto/func_800379C4.c     0x51
 *   src/auto/func_80036D70.c     0x58
 *   asm/code_002800.s            0x00..0x6C offsets reached through the symbol
 */
typedef struct Obj800EFE48 {
    /* 0x00 */ s16  unk_00;
    /* 0x02 */ s16  unk_02;
    /* 0x04 */ s32  unk_04;
    /* 0x08 */ u16  flags_08;     /* the allocation/state bitfield.  Bit 7 means
                                   * "in use": func_8004002C/func_8004006C hand
                                   * out the first record with it clear.
                                   * func_80040410 clears bit 4.  Read 16x. */
    /* 0x0A */ u8   unk_0A;
    /* 0x0B */ u8   unk_0B;
    /* 0x0C */ s32  unk_0C;
    /* 0x10 */ s32  unk_10;
    /* 0x14 */ s16  unk_14;       /* func_80042918/func_8004293C set it to
                                   * (u16 global) - (s8)unk_16 */
    /* 0x16 */ u8   unk_16;       /* read as (s8) in the expression above */
    /* 0x17 */ u8   unk_17;       /* set to a small tag value (1 or 3); read 9x */
    /* 0x18 */ s16  unk_18;
    /* 0x1A */ s16  unk_1A;
    /* 0x1C */ s16  unk_1C;
    /* 0x1E */ s16  unk_1E;
    /* 0x20 */ s32  unk_20;
    /* 0x24 */ s32  unk_24;
    /* 0x28 */ s32  unk_28;
    /* 0x2C */ s32  unk_2C;
    /* 0x30 */ s16  x;            /* 8.8 fixed point, low byte in frac_x */
    /* 0x32 */ s16  y;
    /* 0x34 */ s16  z;
    /* 0x36 */ s16  dx;           /* added to (x,frac_x) each step */
    /* 0x38 */ s16  dy;
    /* 0x3A */ s16  dz;
    /* 0x3C */ s32  unk_3C;
    /* 0x40 */ s32  unk_40;
    /* 0x44 */ s32  unk_44;
    /* 0x48 */ s32  unk_48;
    /* 0x4C */ s32  unk_4C;
    /* 0x50 */ u8   unk_50;
    /* 0x51 */ u8   unk_51;       /* cleared by func_800379C4 */
    /* 0x52 */ char pad_52[0x02];
    /* 0x54 */ s32  unk_54;
    /* 0x58 */ s8   unk_58;       /* func_80036D70 uses it as a *word index*:
                                   * `*(void **)((u8 *)obj + unk_58 * 4)` is a
                                   * cursor it post-increments by 4, then reads a
                                   * little-endian u32 through it byte by byte.
                                   * So the record holds several pointers and
                                   * unk_58 selects one. */
    /* 0x59 */ char pad_59[0x03];
    /* 0x5C */ s32  unk_5C;
    /* 0x60 */ u16  unk_60;
    /* 0x62 */ u8   frac_x;       /* fractional part of x */
    /* 0x63 */ u8   frac_y;
    /* 0x64 */ u8   frac_z;
    /* 0x65 */ u8   unk_65;
    /* 0x66 */ u8   unk_66;
    /* 0x67 */ char pad_67[0x02]; /* 0x68 is read once as a word in the
                                   * disassembly, which would overlap mode_69
                                   * below.  mode_69 is proved by two
                                   * byte-matching files, so it wins and the
                                   * word read is assumed to be a false positive
                                   * of the base-register tracking. */
    /* 0x69 */ u8   mode_69;      /* set from the 2nd argument of func_80040410,
                                   * which clears flags_08 bit 4 at the same
                                   * time; also cleared at asm 0x80016830 */
    /* 0x6A */ char pad_6A[0x02];
    /* 0x6C */ s32  unk_6C;
} Obj800EFE48;                     /* size 0x70 */


/* ===========================================================================
 * SECTION 4 -- fixed-stride arrays
 * =========================================================================== */

/* D_801A7AD8[] -- 0x1C-byte records.
 * Stride proved twice in the disassembly, e.g. at 0x80018420:
 *   `sll v0,v1,3; subu v0,v0,v1; sll v0,v0,2`  ==  n * 7 * 4 == 0x1C.
 * The occupancy test is `lhu 0x16; andi 0x8000` at 0x80018430, matching
 * PLAN.md's "bit 15 of +0x16 means occupied".  func_80024954 (and
 * src/auto/func_80024914.c) is the teardown, and it *clears* that bit --
 * `unk_16 &= 0x7FFF` -- which is the corroboration.
 *
 * Derived from: src/auto/func_80024914.c (0x00, 0x16), asm/code_002800.s.
 *
 * CAUTION: offsets 0x08..0x18 below come from tracking `addu` of an index onto
 * the array base in the disassembly, which is weaker evidence than a
 * byte-matching file, and 0x14 is seen as both `lw` (7x) and part of the `lhu`
 * at 0x16 (69x).  Those cannot both be fields; 0x14 is left as a pad. */
typedef struct Card801A7AD8 {
    /* 0x00 */ s32  unk_00;       /* read 33x, written 4x.  func_80024914 passes
                                   * it to func_8004036C (a release/free-looking
                                   * routine, also called from func_80039F90 over
                                   * a 3-element s32 array) and then zeroes it,
                                   * so it is a handle or pointer. */
    /* 0x04 */ s32  unk_04;
    /* 0x08 */ s16  unk_08;
    /* 0x0A */ s16  unk_0A;
    /* 0x0C */ s16  unk_0C;
    /* 0x0E */ s16  unk_0E;
    /* 0x10 */ s16  unk_10;
    /* 0x12 */ u16  unk_12;
    /* 0x14 */ char pad_14[0x02]; /* seen as `lw` here, which conflicts with the
                                   * u16 at 0x16 -- unresolved, left unnamed */
    /* 0x16 */ u16  flags_16;     /* bit 15 == occupied (see above) */
    /* 0x18 */ u8   unk_18;
    /* 0x19 */ char pad_19[0x03];
} Card801A7AD8;                    /* size 0x1C */

/* D_800EB288[620] -- 0x1C-byte records.  Both the count and the stride come
 * from src/manual/func_80035DB8.c, which byte-matches a `do { ... } while
 * (--n)` over exactly 620 entries of a 0x1C struct.
 * 620 * 0x1C == 0x43D0, so the array spans 0x800EB288..0x800EF658. */
typedef struct Rec800EB288 {
    /* 0x00 */ char pad_00[0x11];
    /* 0x11 */ u8   unk_11;       /* cleared by func_80035DB8 for every record
                                   * whose unk_12 equals its argument + 1 */
    /* 0x12 */ u8   unk_12;       /* the tag/owner compared above */
    /* 0x13 */ char pad_13[0x05];
    /* 0x18 */ u8   unk_18;
    /* 0x19 */ char pad_19[0x03];
} Rec800EB288;                     /* size 0x1C */

/* D_800EA0E8[] -- 0x40-byte records.  Stride from src/manual/func_80029574.c,
 * which byte-matches `&D_800EA0E8[index]` with a 0x40-byte struct.  Offsets
 * seen at 0x68/0x7C/0xE8..0xEC in the disassembly all reduce mod 0x40 to
 * offsets already in this list, which independently confirms the stride.
 * The run of s16 from 0x08 to 0x27 is written by a single initialiser and is
 * most likely a matrix or a vertex list; it is left as a pad. */
typedef struct Rec800EA0E8 {
    /* 0x00 */ s32  unk_00;       /* func_80029574 zeroes 0x04 then 0x00 */
    /* 0x04 */ s32  unk_04;
    /* 0x08 */ char pad_08[0x20]; /* 16 s16 at 0x08,0x0A,...,0x26 */
    /* 0x28 */ u16  unk_28;
    /* 0x2A */ u16  unk_2A;
    /* 0x2C */ s16  unk_2C;
    /* 0x2E */ s16  unk_2E;
    /* 0x30 */ s16  unk_30;
    /* 0x32 */ s16  unk_32;
    /* 0x34 */ s16  unk_34;
    /* 0x36 */ s16  unk_36;
    /* 0x38 */ s16  unk_38;
    /* 0x3A */ u8   unk_3A;
    /* 0x3B */ u8   unk_3B;
    /* 0x3C */ u8   unk_3C;
    /* 0x3D */ char pad_3D[0x03];
} Rec800EA0E8;                     /* size 0x40 */

/* D_800EAD88[8] -- 0x20-byte records, from src/manual/func_8002C5CC.c, which
 * byte-matches a `slot++` scan of exactly 8 records returning the first with
 * bit 7 of +0x1C clear (and NULL if none).  So bit 7 of unk_1C is an
 * in-use flag, on the same pattern as Obj800EFE48.flags_08 bit 7. */
typedef struct Slot800EAD88 {
    /* 0x00 */ char pad_00[0x1C];
    /* 0x1C */ u8   flags_1C;     /* bit 7 == in use */
    /* 0x1D */ char pad_1D[0x03];
} Slot800EAD88;                    /* size 0x20 */

/* D_800EB0F8[] -- 0x64-byte records.  Stride proved by src/manual/
 * func_80035AB8.c: the asm computes ((n*3) << 3 + n) << 2 == n * 100 == 0x64.
 * func_80035AB8 writes four s16 at 0x3C/0x3E/0x40/0x42 from its arguments
 * (note the argument order is 1st->0x3C, 3rd->0x3E, 2nd->0x40, 4th->0x42,
 * which is worth preserving if this ever gets a nicer wrapper).
 * The other offsets are from the disassembly and are less certain. */
typedef struct Rec800EB0F8 {
    /* 0x00 */ s32  unk_00;
    /* 0x04 */ char pad_04[0x0C];
    /* 0x10 */ u8   unk_10;
    /* 0x11 */ u8   unk_11;
    /* 0x12 */ char pad_12[0x01];
    /* 0x13 */ u8   unk_13;
    /* 0x14 */ char pad_14[0x06];
    /* 0x1A */ u8   unk_1A;
    /* 0x1B */ char pad_1B[0x09];
    /* 0x24 */ s32  unk_24;
    /* 0x28 */ s32  unk_28;       /* read as a word.  See the D_800EB184 note
                                   * below -- 0x800EB184 == &D_800EB0F8[1] + 0x28,
                                   * and D_800EB184 is used as a pointer. */
    /* 0x2C */ s32  unk_2C;
    /* 0x30 */ s16  unk_30;
    /* 0x32 */ s16  unk_32;
    /* 0x34 */ u16  unk_34;       /* read 15x, the busiest field */
    /* 0x36 */ s16  unk_36;
    /* 0x38 */ s16  unk_38;
    /* 0x3A */ s16  unk_3A;
    /* 0x3C */ s16  unk_3C;       /* func_80035AB8 arg1 */
    /* 0x3E */ s16  unk_3E;       /* func_80035AB8 arg3 */
    /* 0x40 */ s16  unk_40;       /* func_80035AB8 arg2 */
    /* 0x42 */ s16  unk_42;       /* func_80035AB8 arg4 */
    /* 0x44 */ char pad_44[0x0F];
    /* 0x53 */ u8   unk_53;
    /* 0x54 */ u8   unk_54;
    /* 0x55 */ char pad_55[0x02];
    /* 0x57 */ u8   unk_57;
    /* 0x58 */ char pad_58[0x01];
    /* 0x59 */ u8   unk_59;
    /* 0x5A */ u8   unk_5A;
    /* 0x5B */ u8   unk_5B;
    /* 0x5C */ s16  unk_5C;
    /* 0x5E */ s16  unk_5E;
    /* 0x60 */ char pad_60[0x01];
    /* 0x61 */ u8   unk_61;
    /* 0x62 */ char pad_62[0x02];
} Rec800EB0F8;                     /* size 0x64 */

/* D_800F2C40[] -- 0xE20-byte records.
 * PLAN.md calls these "per-duelist records"; that reading is NOT confirmed
 * here, so the type keeps a neutral name.  What *is* confirmed is the stride.
 * PLAN.md describes it as "n*8-n, <<4, +n, <<5", which evaluates to
 * ((7n) << 4 + n) << 5 == 113n * 32 == 3616n == 0xE20 * n.  Independent
 * confirmation: the disassembly touches the same field set at 0xDC0, 0x1BE0
 * and 0x2A00-relative offsets, i.e. three records at exactly 0xE20 spacing
 * (0xDC0 + 0xE20 == 0x1BE0; 0xE14 + 2*0xE20 == 0x2A54).  At least three
 * records exist; the array bound is not established.
 *
 * A second symbol names the same storage: D_800F39B0 == D_800F2C40 + 0xD70,
 * and src/manual/func_800591C0.c byte-matches `D_800F39B0[row][idx]` with a
 * 16-byte element and a 226-element row -- 226 * 0x10 == 0xE20, the record
 * stride.  So D_800F39B0 is the field at record offset 0xD70, viewed as three
 * 16-byte entries (the function clamps idx to < 3).
 *
 * Derived from:
 *   src/manual/func_80058DD8.c   0xE14, 0xE1F
 *   src/manual/func_80058FB0.c   0xDD0, 0xDD2, 0xDD4, 0xDD6
 *   src/manual/func_80059590.c   0xDC0, 0xDC1, 0xDC2, 0xDC3
 *   src/manual/func_80059AA8.c   0xE12
 *   src/manual/func_800591C0.c   0xD70 (via D_800F39B0)
 *   src/auto/func_8005A4C4.c     0xD18
 *   asm/code_002800.s            the rest
 *
 * Only the tail of the record has been touched at all; 0x000..0xBF3 is
 * completely unexplored, which is why this is a pad and not a field list. */
typedef struct Rec800F2C40 {
    /* 0x0000 */ char pad_0000[0xBF4];
    /* 0x0BF4 */ u8   unk_0BF4;
    /* 0x0BF5 */ u8   unk_0BF5;
    /* 0x0BF6 */ u8   unk_0BF6;
    /* 0x0BF7 */ char pad_0BF7[0x101];
    /* 0x0CF8 */ u16  unk_0CF8;   /* also written with `sw`, so 0x0CF8/0x0CFA may
                                   * really be one 32-bit field */
    /* 0x0CFA */ u16  unk_0CFA;
    /* 0x0CFC */ s32  unk_0CFC;
    /* 0x0D00 */ s32  unk_0D00;
    /* 0x0D04 */ s32  unk_0D04;
    /* 0x0D08 */ s32  unk_0D08;
    /* 0x0D0C */ s32  unk_0D0C;
    /* 0x0D10 */ s32  unk_0D10;
    /* 0x0D14 */ char pad_0D14[0x04];
    /* 0x0D18 */ void *unk_0D18;  /* pointer, null-checked by func_8005A4C4 before
                                   * writing s16 at +0x44/+0x46/+0x48 and s32 at
                                   * +0x18/+0x1C/+0x20 of the target */
    /* 0x0D1C */ char pad_0D1C[0x54];
    /* 0x0D70 */ u8   grp_0D70[0x30]; /* three 16-byte entries; D_800F39B0 names
                                       * this offset (see above) */
    /* 0x0DA0 */ s32  unk_0DA0;
    /* 0x0DA4 */ s32  unk_0DA4;
    /* 0x0DA8 */ s32  unk_0DA8;
    /* 0x0DAC */ char pad_0DAC[0x14];
    /* 0x0DC0 */ u8   unk_0DC0;   /* func_80059590 writes 0x0DC0..0x0DC3 from its
                                   * four arguments, in the order
                                   * arg2->0DC0, arg3->0DC1, arg4->0DC2,
                                   * arg1->0DC3.  Also read as `lb` and once as
                                   * `lw`, so 0x0DC0 may be a 4-byte field read
                                   * whole in some places and per-byte in others. */
    /* 0x0DC1 */ u8   unk_0DC1;
    /* 0x0DC2 */ u8   unk_0DC2;
    /* 0x0DC3 */ u8   unk_0DC3;
    /* 0x0DC4 */ char pad_0DC4[0x04];
    /* 0x0DC8 */ u16  unk_0DC8;
    /* 0x0DCA */ u16  unk_0DCA;
    /* 0x0DCC */ u16  unk_0DCC;
    /* 0x0DCE */ u16  unk_0DCE;
    /* 0x0DD0 */ s16  unk_0DD0;   /* func_80058FB0 copies 0x0DD0..0x0DD6 into a
                                   * caller-supplied u16[4] */
    /* 0x0DD2 */ s16  unk_0DD2;
    /* 0x0DD4 */ s16  unk_0DD4;
    /* 0x0DD6 */ s16  unk_0DD6;
    /* 0x0DD8 */ char pad_0DD8[0x14];
    /* 0x0DEC */ s32  unk_0DEC;
    /* 0x0DF0 */ char pad_0DF0[0x08];
    /* 0x0DF8 */ u16  unk_0DF8;
    /* 0x0DFA */ char pad_0DFA[0x04];
    /* 0x0DFE */ u8   unk_0DFE;
    /* 0x0DFF */ char pad_0DFF[0x07];
    /* 0x0E06 */ u16  unk_0E06;   /* read 12x */
    /* 0x0E08 */ char pad_0E08[0x04];
    /* 0x0E0C */ s32  unk_0E0C;   /* 0x0E0D/0x0E0E/0x0E0F are also read as
                                   * individual bytes -- an unaligned byte view
                                   * of this word, or the word read is spurious */
    /* 0x0E10 */ char pad_0E10[0x01];
    /* 0x0E11 */ u8   unk_0E11;
    /* 0x0E12 */ u8   unk_0E12;   /* func_80059AA8 returns the old value and
                                   * overwrites it when its 2nd arg is >= 0 */
    /* 0x0E13 */ char pad_0E13[0x01];
    /* 0x0E14 */ u8   unk_0E14;   /* func_80058DD8 returns 2 unless this is 0xFF */
    /* 0x0E15 */ u8   unk_0E15;
    /* 0x0E16 */ char pad_0E16[0x09];
    /* 0x0E1F */ u8   unk_0E1F;   /* func_80058DD8 returns (unk_0E1F != 0) */
} Rec800F2C40;                     /* size 0xE20 -- unk_0E1F is the last byte */

/* D_801AB000[] -- 0xC-byte records.  Stride from src/manual/func_80070870.c
 * and src/manual/func_800708C4.c, which byte-match `D_801AB000[i]` with a
 * 0xC-byte struct while reading offsets 0x00 and 0x08 respectively. */
typedef struct Rec801AB000 {
    /* 0x00 */ s16  unk_00;       /* read 14x, always signed */
    /* 0x02 */ s16  unk_02;
    /* 0x04 */ s16  unk_04;
    /* 0x06 */ u16  unk_06;       /* read 16x, always unsigned */
    /* 0x08 */ s8   unk_08;       /* read as lb, so genuinely signed */
    /* 0x09 */ s8   unk_09;
    /* 0x0A */ char pad_0A[0x01];
    /* 0x0B */ u8   unk_0B;
} Rec801AB000;                     /* size 0xC */

/* D_800917F0[] -- 9-byte records, from src/manual/func_80070710.c
 * (`D_800917F0[D_8009B361].unk00`, struct size 9).  Note 0x800917F0 lies inside
 * the trailing rodata region PLAN.md describes at 0x800906E0..0x80092C00, so
 * this is a constant table, not writable state. */
typedef struct Rec800917F0 {
    /* 0x00 */ s8   unk_00;       /* read as lb */
    /* 0x01 */ s8   unk_01;
    /* 0x02 */ char pad_02[0x07];
} Rec800917F0;                     /* size 9 */

/* D_801798A8[][5] -- rows of five {s16 limit; s16 value} pairs, i.e. a row
 * stride of 0x14.  From src/manual/func_80021558.c, which byte-matches a
 * sentinel-terminated scan: walk the row until `value < limit`, then return the
 * paired value.  There is no bound check, so the last entry's limit must be a
 * catch-all -- that is what makes the "threshold table" reading safe. */
typedef struct Threshold {
    /* 0x00 */ s16  limit;
    /* 0x02 */ s16  value;
} Threshold;                       /* size 4 */

/* D_800F5918[0x50] -- 8-byte pairs.
 *
 * ***** GENUINE CONTRADICTION BETWEEN TWO BYTE-MATCHING FILES *****
 * src/manual/func_800601D0.c calls +0x00 the key and +0x04 the value: it scans
 * 0x50 slots for `slot->key == arg` and returns `slot->value`.
 * src/manual/func_80060170.c does the opposite: it scans +0x04 for `arg0`, and
 * on the first slot with both words zero writes arg0 to +0x04 and arg1 to +0x00.
 * Both byte-match (verified against asm 0x800601D0 and 0x80060170).
 *
 * They are consistent only if the table is a two-way association rather than a
 * key/value map: func_80060170(b, a) inserts the pair, func_800601D0(a) looks
 * up by the +0x00 word and returns the +0x04 word.  The `key`/`value` names in
 * func_800601D0.c are therefore an interpretive error, not a layout error --
 * which is exactly why the fields are unnamed here.
 *
 * A zero word in either slot means "free" (func_80060170 requires both zero).
 * func_800601D0 additionally rejects `&GsU_00000000` as a lookup argument, so
 * the +0x00 word holds addresses. */
typedef struct Pair800F5918 {
    /* 0x00 */ s32  unk_00;       /* searched by func_800601D0; written by
                                   * func_80060170 from its 2nd argument */
    /* 0x04 */ s32  unk_04;       /* searched by func_80060170; returned by
                                   * func_800601D0 */
} Pair800F5918;                    /* size 8 */
#define PAIR_800F5918_COUNT 0x50   /* both functions iterate exactly 0x50 times */


/* ===========================================================================
 * SECTION 5 -- D_800E9EC8: the control block used by the 0x80015xxx module
 * ===========================================================================
 * A single static block (not an array).  PLAN.md lists it as "a pad/controller
 * block"; **that is not supported by anything found here** and should be
 * treated as retracted until someone produces evidence.  What the code shows:
 *
 *   - func_80015998 spins on `func_80012D4C()` while bit 7 of unk_06 is set,
 *     so unk_06 bit 7 is a "busy" flag.
 *   - unk_06 is otherwise OR-ed with 1, 2, 6, 0x30, or assigned 0x80 / 0xB0.
 *   - unk_07 is set to 8 or 0xC -- a small count, set alongside a start.
 *   - unk_08 is set to 0xFF and to 0.
 *   - unk_00 is a 32-bit value whose special case is 0xFFFFFF (24 bits set);
 *     func_8001581C/func_80015944 set a separate flag when their argument
 *     equals 0xFFFFFF, and func_80015870 stores 0xFFFFFF here directly.
 *   - the enclosing module (0x800151B0..0x80015D0C) calls GsSortBoxFill, and
 *     func_80015780/func_80015870 write RGB-looking byte triples to
 *     gp+0x23A..0x23C and gp+0x242..0x244.
 *
 * Taken together that reads like a screen fade / colour-flash controller with a
 * 24-bit colour at +0x00, a level at +0x08 and a step count at +0x07 -- but
 * that is an inference from the surrounding calls, not a proof, and the field
 * names below stay neutral.  Two earlier workers guessed differently and named
 * the same struct `Pad800E9EC8` (func_800158B8.c, func_80015CC0.c) and
 * `Sound` (func_80015904.c); neither guess is supported either.
 *
 * Extent: func_800156B8 byte-matches a loop that writes offsets 0x0A..0x27
 * (`for (i = 0x1D; i >= 0; i--) base[i + 0x0A] = value;`).  The nearest
 * higher symbol is D_800E9FF0, so the block is at most 0x128 bytes; only
 * 0x00..0x27 is accounted for.
 *
 * Derived from: src/manual/func_800151B0.c, func_800156B8.c, func_800157DC.c,
 *   func_8001581C.c, func_800158B8.c, func_80015904.c, func_80015944.c,
 *   func_80015998.c, func_80015C84.c, func_80015CC0.c, and asm/code_002800.s.
 */
typedef struct Unk800E9EC8 {
    /* 0x00 */ s32  unk_00;       /* 24-bit value; 0xFFFFFF is a sentinel */
    /* 0x04 */ u8   unk_04;       /* passed to func_800156B8 as the fill byte */
    /* 0x05 */ u8   unk_05;       /* set to 0 and to 0xFF */
    /* 0x06 */ u8   flags_06;     /* bit 7 == busy (spun on by func_80015998) */
    /* 0x07 */ u8   unk_07;       /* small count: 8 or 0xC */
    /* 0x08 */ s16  unk_08;       /* set to 0xFF and to 0 */
    /* 0x0A */ u8   tbl_0A[0x1E]; /* 30 bytes, filled with unk_04 by func_800156B8 */
    /* 0x28 */ char pad_28[0x100]; /* unexplored; the block cannot extend past
                                    * D_800E9FF0 == this + 0x128 */
} Unk800E9EC8;                     /* size >= 0x28, at most 0x128 */


/* ===========================================================================
 * SECTION 6 -- D_800F5BE8: a byte-stream reader that shares storage with tables
 * ===========================================================================
 * Three byte-matching files describe this address three different ways, and
 * they do NOT overlap, so all three are simultaneously true -- it is one
 * compound object, not a contradiction:
 *
 *   src/manual/func_8007058C.c   `*D_800F5BE8.pos++` with pos at +0x08
 *   src/manual/func_80070870.c   `u16 D_800F5BE8[]`, reads indices 0x1F..0x3E
 *                                == bytes 0x3E..0x7D
 *   src/manual/func_800708C4.c   `u8 D_800F5BE8[]`, reads indices 0x7E..0x96
 *
 * The two array views are exactly adjacent (0x3E..0x7D then 0x7E..0x96), which
 * is good evidence they are two real neighbouring tables rather than an
 * accident.  Note that func_8007058C.c declares `s32 unk0; s32 unk4;` in front
 * of `pos` -- those are padding, not evidence; the disassembly reads 0x00 and
 * 0x01 as single bytes.
 */
typedef struct Reader800F5BE8 {
    /* 0x00 */ u8   unk_00;
    /* 0x01 */ u8   unk_01;
    /* 0x02 */ char pad_02[0x02];
    /* 0x04 */ s32  unk_04;
    /* 0x08 */ u8  *pos;          /* read cursor: func_8007058C returns *pos++ */
    /* 0x0C */ s32  unk_0C;
    /* 0x10 */ char pad_10[0x04];
    /* 0x14 */ u8   unk_14;
    /* 0x15 */ char pad_15[0x03];
    /* 0x18 */ s32  unk_18;
    /* 0x1C */ char pad_1C[0x1C];
    /* 0x38 */ u8   unk_38;
    /* 0x39 */ u8   unk_39;
    /* 0x3A */ char pad_3A[0x04];
    /* 0x3E */ u16  tbl_3E[0x20]; /* 0x3E..0x7D; func_80070870 scans all 32 for a
                                   * match against Rec801AB000.unk_00 */
    /* 0x7E */ u8   tbl_7E[0x19]; /* 0x7E..0x96; func_800708C4 scans all 25 for a
                                   * match against Rec801AB000.unk_08 + 1 */
    /* 0x97 */ char pad_97[0x01];
    /* 0x98 */ u16  unk_98;
    /* 0x9A */ u8   unk_9A;
    /* 0x9B */ u8   unk_9B;
    /* 0x9C */ u8   unk_9C;
    /* 0x9D */ u8   unk_9D;
    /* 0x9E */ u8   unk_9E;
    /* 0x9F */ char pad_9F[0x01];
    /* 0xA0 */ u16  unk_A0;
    /* 0xA2 */ u8   unk_A2;       /* read 18x, the busiest byte in the block */
    /* 0xA3 */ u8   unk_A3;
    /* 0xA4 */ u8   unk_A4;
    /* 0xA5 */ char pad_A5[0x05];
    /* 0xAA */ u8   unk_AA;
    /* 0xAB */ char pad_AB[0x01];
} Reader800F5BE8;                  /* size >= 0xAC; total extent unknown */


/* ===========================================================================
 * SECTION 7 -- pointer-passed structs that are NOT (yet) any of the above
 * ===========================================================================
 * These come from byte-matching functions that take an anonymous pointer.  They
 * are kept separate because their offsets *conflict* with the object pool
 * record in section 3, which is strong evidence they are different types.
 */

/* From src/manual/func_80039A14.c and src/manual/func_80039A60.c (both
 * byte-matching, and they agree with each other).  Offset 0x34 is a u16
 * bitfield: the caller ORs in 0x800 or 0xA00, then spins on func_800393B0
 * until bit 0x2000 appears -- a request/completion handshake.
 *
 * CONFLICT WORTH KNOWING: Obj800EFE48 uses 0x34 as the s16 `z` coordinate
 * (func_80042A50, byte-matching).  Both cannot be the same type.  The
 * 0x80039xxx and 0x80042xxx functions are in different modules, so the most
 * likely explanation is two distinct structs -- but it is also possible one of
 * the two readings is wrong, and nothing here settles it. */
typedef struct Unk80039A14 {
    /* 0x00 */ char pad_00[0x34];
    /* 0x34 */ u16  flags_34;     /* request bits 0x800 / 0xA00 in, done bit
                                   * 0x2000 out */
    /* 0x36 */ char pad_36[0x02];
} Unk80039A14;                     /* size 0x38 as declared; the real object is
                                    * at least 0x36 bytes and probably larger */

/* From src/manual/func_80039AAC.c: test-and-set of bit 7 of the byte at 0x13,
 * returning 1 if it was already set.  A lock or "already queued" guard.
 * src/manual/func_80039F1C.c is the same routine over the byte at 0x33.
 * Two different offsets, two byte-matching files -- so either the module has
 * two such guards in one struct, or these are two types.  Both are recorded. */
typedef struct Unk80039AAC {
    /* 0x00 */ char pad_00[0x13];
    /* 0x13 */ u8   flags_13;     /* bit 7, test-and-set (func_80039AAC) */
    /* 0x14 */ char pad_14[0x1F];
    /* 0x33 */ u8   flags_33;     /* bit 7, test-and-set (func_80039F1C) */
    /* 0x34 */ char pad_34[0x04];
} Unk80039AAC;                     /* size 0x38 as declared; the real object is
                                    * at least 0x34 bytes, and the two flag bytes
                                    * may not belong to the same object at all */

/* From src/manual/func_8001B780.c and src/manual/func_8003A920.c, which agree:
 * a struct with an s16 pair at 0x30/0x32 written together.  func_8003A920
 * writes them through a 3-element array of pointers (`arg0[i]->unk30 = arg1`),
 * func_8001B780 through a pointer field at 0x04 of its own argument.
 * 0x30/0x32 also line up with Obj800EFE48.x/.y, so this may be that same type
 * seen from a different call site -- unconfirmed. */
typedef struct Unk8003A920 {
    /* 0x00 */ char pad_00[0x30];
    /* 0x30 */ s16  unk_30;
    /* 0x32 */ s16  unk_32;
} Unk8003A920;                     /* size 0x34 as declared; the real object is
                                    * at least 0x34 bytes and probably larger */

/* From src/manual/func_8004BAE4.c: a small cursor object handed to the sound
 * driver's stream reader.  0x00 is a byte offset into SoundWork.unk_7DC and
 * 0x24 is set to 1 when the read runs past SoundWork.unk_7EC. */
typedef struct StreamCursor {
    /* 0x00 */ s32  pos;          /* byte offset; post-incremented per read */
    /* 0x04 */ char pad_04[0x20];
    /* 0x24 */ u8   eof;          /* set to 1 on overrun; the read returns -1 */
} StreamCursor;                    /* size >= 0x25 */


/* ===========================================================================
 * SECTION 8 -- globals
 * ===========================================================================
 * Each entry gives the absolute symbol, the equivalent `gp + N` form, and the
 * files that establish its width.  Remember GP_BASE == 0x8009AF08, so
 * `D_8009B145` and `0x23D($gp)` are the same byte.
 *
 * READ THE HAZARD NOTE AT THE TOP before using these declarations in a file
 * that currently matches: the declared width decides whether the reference
 * comes out gp-relative or as a %hi/%lo pair.
 *
 * On signedness.  An 8-bit load has distinct encodings (`lb` vs `lbu`), so a
 * byte-matching *read* pins the signedness while a *write* (`sb`) does not.
 * Where two files disagree, the one that reads wins and the loser is noted.
 * ---------------------------------------------------------------------------
 */

/* --- the two state pointers ------------------------------------------------ */
extern SoundWork *D_8009B458;       /* gp + 0x550; == SOUND_WORK_ADDR */
extern GameState *D_8009B45C;       /* gp + 0x554; == GAME_STATE_ADDR */
/* gp + 0x558 (D_8009B460) holds GAME_STATE_ADDR + 0x1650, i.e. a pointer to
 * whatever object follows GameState.  Not declared: its type is unknown. */

/* --- small-data scalars, ordered by address -------------------------------- */
extern u16 D_8009AF76;   /* gp + 0x06E  src/auto/func_80042918.c */
extern u16 D_8009AF7A;   /* gp + 0x072  src/auto/func_8004293C.c */
extern s16 D_8009AF92;   /* gp + 0x08A  src/auto/func_80059AE0.c */
extern s8  D_8009AF94;   /* gp + 0x08C  src/manual/func_80059C9C.c */
extern s16 D_8009AF96;   /* gp + 0x08E  src/auto/func_80059C18.c */
extern s8  D_8009AF9A;   /* gp + 0x092  compared against -2, so genuinely signed
                          *             (src/auto/func_80059C88.c, func_80059CD0.c) */
extern u8  D_8009AFA0;   /* gp + 0x098  src/auto/func_80058DCC.c */
extern s8  D_8009AFA4;   /* gp + 0x09C  src/auto/func_80059AEC.c */
extern s8  D_8009B064;   /* gp + 0x15C  src/auto/func_8005C5C4.c */
extern s32 D_8009B074;   /* gp + 0x16C  src/auto/func_8005FAE4.c, func_8005FB14.c */
extern u8  D_8009B078;   /* gp + 0x170  read as u8 by func_8005FB08/func_8005FB14;
                          *             func_8005FAE4 only stores, so its `s8` is
                          *             not evidence */
extern s8  D_8009B079;   /* gp + 0x171  store-only; signedness unconstrained */
extern s8  D_8009B07A;   /* gp + 0x172  set to -1 by func_8005FAE4 */
extern u8  D_8009B07B;   /* gp + 0x173  returned as u8 by func_8005F174 */
extern u8  D_8009B07C;   /* gp + 0x174  returned as u8 by func_8005F18C */
extern s32 D_8009B0B8;   /* gp + 0x1B0  src/manual/func_800134B4.c */
extern u8  D_8009B0C0;   /* gp + 0x1B8  src/manual/func_8002CD8C.c */
extern s32 D_8009B0E8;   /* gp + 0x1E0  src/auto/func_80013898.c */
extern s32 D_8009B0F0;   /* gp + 0x1E8  holds a function address (func_8004666C is
                          *             stored here at asm 0x800467AC) */
extern u32 D_8009B0F4;   /* gp + 0x1EC  hardware-ish status word, tested against
                          *             the mask 0x02000030.  DISAGREEMENT: declared
                          *             `volatile u32` in func_80014FA4.c and plain
                          *             `s32` in func_800438B8.c / func_80013898.c,
                          *             and all three byte-match. */
extern s32 D_8009B0FC;   /* gp + 0x1F4  src/auto/func_80013898.c */
extern s8  D_8009B108;   /* gp + 0x200  store-only */
extern s32 D_8009B10C;   /* gp + 0x204 */
extern s8  D_8009B110;   /* gp + 0x208  store-only */
extern u16 D_8009B112;   /* gp + 0x20A  read-modify-written as u16 by func_80015010
                          *             (`&= 0x3FFC; |= 2`).  That function needs
                          *             `volatile` to match -- without it GCC merges
                          *             the two operations and comes out three
                          *             instructions short.  func_80013898.c stores 0
                          *             here and declares plain `s16`. */
extern s32 D_8009B118;   /* gp + 0x210 */
extern s32 D_8009B120;   /* gp + 0x218  holds a function address (func_800466C8 at
                          *             asm 0x800467C0) */
extern s16 D_8009B124;   /* gp + 0x21C */
extern void (*D_8009B128)(void); /* gp + 0x220  src/manual/func_8004545C.c assigns
                                  *             D_8004544C to it -- a callback slot */
extern s32 D_8009B12C;   /* gp + 0x224 */
extern s32 D_8009B130;   /* gp + 0x228 */
extern u32 D_8009B134;   /* gp + 0x22C  same volatile disagreement as D_8009B0F4 */
extern s8  D_8009B141;   /* gp + 0x239  src/gp_probe.c, src/auto/func_80015D0C.c.
                          *             The first `$gp` function ever matched. */
extern u8  D_8009B145;   /* gp + 0x23D  set to 1 when the 0x800E9EC8 block's
                          *             unk_00 argument is 0xFFFFFF; tested by
                          *             func_80015870 */
extern u8  D_8009B254;   /* gp + 0x34C  src/manual/func_8002CD8C.c */
extern u8  D_8009B260;   /* gp + 0x358  src/auto/func_8002C68C.c */
extern s8  D_8009B2B4;   /* gp + 0x3AC  the 0x8009B2B4..0x8009B2EC group is written
                          *             en bloc by src/auto/func_80030250.c */
extern s8  D_8009B2B5;   /* gp + 0x3AD */
extern s8  D_8009B2B6;   /* gp + 0x3AE */
extern s8  D_8009B2B8;   /* gp + 0x3B0 */
extern s8  D_8009B2C0;   /* gp + 0x3B8 */
extern s8  D_8009B2C1;   /* gp + 0x3B9 */
extern s8  D_8009B2C2;   /* gp + 0x3BA */
extern s8  D_8009B2DC;   /* gp + 0x3D4 */
extern s8  D_8009B2E0;   /* gp + 0x3D8 */
extern s8  D_8009B2E9;   /* gp + 0x3E1 */
extern s8  D_8009B2EA;   /* gp + 0x3E2 */
extern s32 D_8009B2EC;   /* gp + 0x3E4 */
extern s8  D_8009B318;   /* gp + 0x410  src/auto/func_80035A58.c */
extern s8  D_8009B361;   /* gp + 0x459  index into D_800917F0[]
                          *             (src/manual/func_80070710.c) */
extern u8  D_8009B37C;   /* gp + 0x474  src/manual/func_8003C8CC.c */
extern u16 D_8009B394;   /* gp + 0x48C  the 0x8009B394..0x8009B3AC group is a run of
                          *             u16 copied around by src/auto/func_8003CDF8.c
                          *             and func_8003CE48.c */
extern u16 D_8009B396;   /* gp + 0x48E */
extern u16 D_8009B398;   /* gp + 0x490  tested against the mask 0x8C0 in
                          *             src/auto/func_800438B8.c */
extern u16 D_8009B39A;   /* gp + 0x492 */
extern u8  D_8009B39C;   /* gp + 0x494  set to 0x18 by func_8002CD8C with `sb`, so
                          *             u8 is what that file needed -- but every
                          *             neighbour in this run is u16, so 0x494 may
                          *             really be the low byte of a halfword */
extern u16 D_8009B39E;   /* gp + 0x496 */
extern u16 D_8009B3A0;   /* gp + 0x498 */
extern u8  D_8009B3A2;   /* gp + 0x49A  set to 0x14 by func_8002CD8C; same
                          *             byte-vs-halfword caveat as D_8009B39C */
extern u16 D_8009B3A4;   /* gp + 0x49C  declared `volatile u16` in
                          *             src/manual/func_80023FBC.c and plain `u16`
                          *             in src/auto/func_8003CDF8.c; both match */
extern u16 D_8009B3A6;   /* gp + 0x49E */
extern u16 D_8009B3AC;   /* gp + 0x4A4 */
extern u8  D_8009B3C1;   /* gp + 0x4B9  src/manual/func_8003F740.c */
extern u8  D_8009B3C6;   /* gp + 0x4BE  src/manual/func_8003E46C.c */
extern u8  D_8009B3DE;   /* gp + 0x4D6  src/manual/func_8003F740.c */
extern u8  D_8009B3EF;   /* gp + 0x4E7  src/manual/func_8003F70C.c */
extern u16 D_8009B3FA;   /* gp + 0x4F2  a status/request word: func_8003E46C does
                          *             `(x & 0xFF87) | arg | 0x80` with two separate
                          *             stores, func_8003F740 sets 0x8000,
                          *             func_8003F70C treats non-zero as "busy".
                          *             DISAGREEMENT: `volatile u16` in
                          *             func_8003E46C.c, plain `u16` in
                          *             func_8003F70C.c and func_8003F740.c. */
extern s32 D_8009B400;   /* gp + 0x4F8  src/auto/func_8003FF08.c */

/* --- arrays and blocks (all addressed with %hi/%lo, not through $gp) ------- */
extern s32          D_800E9DB0[4];      /* zeroed 3..0 by func_800134B4 */
extern Unk800E9EC8  D_800E9EC8;         /* section 5 */
extern Rec800EA0E8  D_800EA0E8[];       /* 0x40 stride; count unknown */
extern Slot800EAD88 D_800EAD88[8];
extern u8           D_800EAF08[0xF0];   /* byte table; func_80035CA8 clears every
                                         * entry equal to its argument + 1 */
extern Rec800EB0F8  D_800EB0F8[];       /* 0x64 stride; count unknown */
extern void        *D_800EB184;         /* used as a pointer by func_800300AC, which
                                         * writes 0x80 to bytes +0x0C/+0x0D/+0x0E of
                                         * the target.  UNRESOLVED: this address is
                                         * D_800EB0F8 + 0x8C == &D_800EB0F8[1].unk_28,
                                         * so either D_800EB0F8[] is not an array all
                                         * the way up, or splat has given a name to
                                         * one record's pointer field.  Both readings
                                         * fit the bytes. */
extern Rec800EB288  D_800EB288[620];
extern Obj800EFE48  D_800EFE48[0x60];   /* the object pool, section 3 */
extern Obj800EFE48  D_800F0548[];       /* == &D_800EFE48[0x10]; see section 3 */
extern Rec800F2C40  D_800F2C40[];       /* 0xE20 stride; >= 3 records */
extern u8           D_800F39B0[];       /* == D_800F2C40 + 0xD70; see section 4 */
extern Pair800F5918 D_800F5918[PAIR_800F5918_COUNT];
extern Reader800F5BE8 D_800F5BE8;       /* section 6 */
extern Rec800917F0  D_800917F0[];       /* rodata table, 9-byte stride */
extern Threshold    D_801798A8[][5];
extern Rec801AB000  D_801AB000[];       /* 0xC stride; count unknown */
extern Card801A7AD8 D_801A7AD8[];       /* 0x1C stride; asm 0x80018450 bounds one
                                         * loop over it at 0xA, but that is a
                                         * per-caller limit, not the array size */
extern u16          D_801D0200[];       /* func_8002C4DC searches the first 0x28
                                         * halfwords for a key and returns its index.
                                         * func_8003F87C copies 0x680 bytes from here
                                         * to D_801D3200 as u8, so the same storage is
                                         * read at both widths. */
extern u8           D_801D3200[];       /* destination of that copy.  Note
                                         * func_8003F87C also passes
                                         * `D_801D3200 - 0x200` to func_8003D03C, so
                                         * something lives immediately below it. */

#endif /* GAME_H */
