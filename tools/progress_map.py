"""Draw decompilation progress as a PNG grid, one cell per function.

Function counts flatter the progress -- a 6-instruction leaf scores the same
as a 400-instruction state machine -- so the header also reports matched
instructions, which is the honest measure of how much of the game is done.

Cells are laid out strictly by address, so a given function keeps the same
cell across runs and two maps can be diffed by eye.  $gp users get their own
colour: they are not hard, they are blocked until the small-data layout is
reconstructed, and lumping them in with plain TODO hides that.

    py -3 tools/progress_map.py
    py -3 tools/progress_map.py --cell 8 --cols 96 --out docs/progress.png
"""
import argparse
import glob
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
from funcs import parse, GAME_END                                  # noqa: E402
from match import asm_inventory                                    # noqa: E402

SYMBOLS = os.path.join(REPO, "config", "symbol_addrs.txt")

# A definition is a name, a parenthesised parameter list (one level of nesting,
# enough for function-pointer parameters) and then an opening brace.  The brace
# is what separates it from the m2c forward declarations, which end in ';'.
DEFN = re.compile(r"\b([A-Za-z_]\w*)\s*\((?:[^()]|\([^()]*\))*\)\s*\{")
SYMBOL = re.compile(r"^(\S+)\s*=\s*0x([0-9A-Fa-f]+)\s*;.*type:func")

BG        = (255, 255, 255)
FG        = ( 32,  32,  32)
MUTED     = (110, 110, 110)
C_MATCHED = ( 46, 158,  79)
C_GP      = (232, 160,  42)
C_TODO    = (255, 255, 255)
C_TODO_E  = (203, 203, 203)
C_SDK     = (122, 140, 160)

MARGIN = 24


def source_definitions(inv):
    """Names in the disassembly inventory that some src/**/*.c defines."""
    found = set()
    for path in sorted(glob.glob(os.path.join(REPO, "src", "**", "*.c"),
                                 recursive=True)):
        text = open(path, encoding="utf-8", errors="replace").read()
        found |= {m.group(1) for m in DEFN.finditer(text)} & set(inv)
        # One function per file under src/auto, named after it.  Trusting the
        # filename catches declarators the regex above cannot parse, such as
        # func_800603DC, which returns a pointer to a function.
        if os.path.basename(os.path.dirname(path)) == "auto":
            stem = os.path.splitext(os.path.basename(path))[0]
            if stem in inv:
                found.add(stem)
    return found


def sdk_named():
    """SDK functions already identified by signature match."""
    if not os.path.exists(SYMBOLS):
        return set()
    names = set()
    for line in open(SYMBOLS):
        m = SYMBOL.match(line.strip())
        if m and int(m.group(2), 16) >= GAME_END:
            names.add(m.group(1))
    return names


def load_font(size):
    for path in (r"C:\Windows\Fonts\segoeui.ttf",
                 r"C:\Windows\Fonts\arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def line_height(font):
    ascent, descent = font.getmetrics()
    return ascent + descent


def pct(part, whole):
    return (part / whole * 100) if whole else 0.0


def grid_height(count, cols, cell, gap):
    rows = (count + cols - 1) // cols
    return rows * (cell + gap) - gap if rows else 0


def draw_grid(draw, items, x0, y0, cols, cell, gap):
    """items is a list of (fill, outline); returns the y below the grid."""
    for i, (fill, outline) in enumerate(items):
        x = x0 + (i % cols) * (cell + gap)
        y = y0 + (i // cols) * (cell + gap)
        draw.rectangle([x, y, x + cell - 1, y + cell - 1],
                       fill=fill, outline=outline)
    return y0 + grid_height(len(items), cols, cell, gap)


def draw_legend(draw, entries, x0, y0, font, box):
    x = x0
    for fill, outline, label in entries:
        draw.rectangle([x, y0, x + box - 1, y0 + box - 1],
                       fill=fill, outline=outline)
        x += box + 6
        draw.text((x, y0 + (box - line_height(font)) // 2 - 1), label,
                  font=font, fill=MUTED)
        x += draw.textlength(label, font=font) + 22


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, default=12, help="cell size in pixels")
    ap.add_argument("--gap", type=int, default=2, help="gap between cells")
    ap.add_argument("--cols", type=int, default=64, help="cells per row")
    ap.add_argument("--out", default=os.path.join(REPO, "progress.png"))
    ap.add_argument("--no-sdk", action="store_true",
                    help="omit the Psy-Q SDK band")
    args = ap.parse_args()

    inv = asm_inventory()
    funcs = parse()
    matched = source_definitions(inv)

    game = sorted([f for f in funcs if f["addr"] < GAME_END],
                  key=lambda f: f["addr"])
    sdk = sorted([f for f in funcs if f["addr"] >= GAME_END],
                 key=lambda f: f["addr"])

    for f in game:
        if f["name"] in matched:
            f["status"] = "matched"
        elif f["gp"]:
            f["status"] = "gp"
        else:
            f["status"] = "todo"

    n_matched = sum(1 for f in game if f["status"] == "matched")
    n_gp = sum(1 for f in game if f["status"] == "gp")
    n_todo = sum(1 for f in game if f["status"] == "todo")
    ins_total = sum(f["insns"] for f in game)
    ins_matched = sum(f["insns"] for f in game if f["status"] == "matched")
    ins_gp = sum(f["insns"] for f in game if f["status"] == "gp")
    named = len(sdk_named())

    print("game functions:    %d total" % len(game))
    print("  matched:         %d (%.2f%%)" % (n_matched, pct(n_matched, len(game))))
    print("  blocked on $gp:  %d (%.2f%%)" % (n_gp, pct(n_gp, len(game))))
    print("  todo:            %d (%.2f%%)" % (n_todo, pct(n_todo, len(game))))
    print("game instructions: %d total" % ins_total)
    print("  matched:         %d (%.2f%%)" % (ins_matched, pct(ins_matched, ins_total)))
    print("  blocked on $gp:  %d (%.2f%%)" % (ins_gp, pct(ins_gp, ins_total)))
    print("sdk functions:     %d (%d identified by signature, none decompiled)"
          % (len(sdk), named))

    cell, gap, cols = args.cell, args.gap, args.cols
    title_font = load_font(20)
    body_font = load_font(14)
    small_font = load_font(12)

    head = [
        "functions:    %d / %d matched (%.2f%%)"
        % (n_matched, len(game), pct(n_matched, len(game))),
        "instructions: %d / %d matched (%.2f%%)"
        % (ins_matched, ins_total, pct(ins_matched, ins_total)),
        "blocked on $gp: %d functions, %d instructions (%.2f%% of game code)"
        % (n_gp, ins_gp, pct(ins_gp, ins_total)),
    ]
    legend = [(C_MATCHED, C_MATCHED, "matched"),
              (C_GP, C_GP, "todo, blocked on $gp"),
              (C_TODO, C_TODO_E, "todo")]
    if not args.no_sdk:
        legend.append((C_SDK, C_SDK, "Psy-Q SDK (not decompiled)"))

    # Measure first, then size the canvas, so nothing has to be clipped.
    title_h = line_height(title_font)
    body_h = line_height(body_font)
    small_h = line_height(small_font)

    width = MARGIN * 2 + cols * (cell + gap) - gap
    y = MARGIN + title_h + 10
    y += len(head) * (body_h + 4) + 8
    y += cell + 8 + 12
    y += small_h + 6
    game_top = y
    y += grid_height(len(game), cols, cell, gap)
    if not args.no_sdk:
        y += 18 + small_h + 6
        sdk_top = y
        y += grid_height(len(sdk), cols, cell, gap)
    height = y + MARGIN

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    y = MARGIN
    draw.text((MARGIN, y), "%s -- decompilation progress" % os.path.basename(REPO),
              font=title_font, fill=FG)
    y += title_h + 10
    for line in head:
        draw.text((MARGIN, y), line, font=body_font, fill=FG)
        y += body_h + 4
    y += 8
    draw_legend(draw, legend, MARGIN, y, small_font, cell)

    draw.text((MARGIN, game_top - small_h - 6),
              "game code  0x%08X - 0x%08X, %d functions, ordered by address"
              % (game[0]["addr"], GAME_END, len(game)),
              font=small_font, fill=MUTED)
    style = {"matched": (C_MATCHED, C_MATCHED),
             "gp": (C_GP, C_GP),
             "todo": (C_TODO, C_TODO_E)}
    draw_grid(draw, [style[f["status"]] for f in game],
              MARGIN, game_top, cols, cell, gap)

    if not args.no_sdk:
        draw.text((MARGIN, sdk_top - small_h - 6),
                  "Psy-Q SDK  0x%08X and above, %d functions -- identified by "
                  "signature (%d named), NOT decompiled" % (GAME_END, len(sdk), named),
                  font=small_font, fill=MUTED)
        draw_grid(draw, [(C_SDK, C_SDK)] * len(sdk),
                  MARGIN, sdk_top, cols, cell, gap)

    out = os.path.abspath(args.out)
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    img.save(out, "PNG")
    print("\nwrote %s (%dx%d)" % (out, width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
