#!/usr/bin/env python3
"""Draw one image that sums up the world news of Wednesday 25 November 2026.

Standard library only. The picture is rendered pixel by pixel from fixed
data, so every run writes exactly the same bytes to /output/entry.png.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (32, 36, 46)
RED = (179, 49, 42)
NAVY = (39, 65, 86)
SEA = (127, 168, 184)
DEEP = (62, 107, 126)
SAND = (217, 201, 163)
GREY = (110, 116, 124)
WHITE = (252, 250, 244)
FLAME = (232, 119, 44)
YELLOW = (240, 190, 60)
GREEN = (84, 128, 76)

# ------------------------------------------------------------- 5x7 font
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
}

# ------------------------------------------------------------- canvas
PX = bytearray(W * H * 3)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = c[0]
        PX[i + 1] = c[1]
        PX[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(xx, yy, c)


def frame(x, y, w, h, t, c):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                put(xx, yy, c)


def line(x0, y0, x1, y1, t, c):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        for dy in range(-(t // 2), t - t // 2):
            for dx in range(-(t // 2), t - t // 2):
                put(x + dx, y + dy, c)


def text_w(s, scale, track):
    return len(s) * (5 * scale + track) - track


def draw_text(x, y, s, scale, c, track=None):
    if track is None:
        track = scale
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "#":
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 5 * scale + track
    return cx - track


def centered(y, s, scale, c, track=None):
    if track is None:
        track = scale
    x = (W - text_w(s, scale, track)) // 2
    return draw_text(x, y, s, scale, c, track)


def wrap(s, scale, max_w, track=None):
    if track is None:
        track = scale
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale, track) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def block(x, y, s, scale, c, max_w, leading=None, center=False):
    if leading is None:
        leading = 7 * scale + scale * 2
    for ln in wrap(s, scale, max_w):
        if center:
            draw_text(x + (max_w - text_w(ln, scale, scale)) // 2, y, ln, scale, c)
        else:
            draw_text(x, y, ln, scale, c)
        y += leading
    return y


# ------------------------------------------------------------- scenes
def port_scene(x, y, w, h):
    """A factory and a container port under a new-tariff sign."""
    rect(x, y, w, h, SEA)
    rect(x, y, w, 34, NAVY)                       # sky band
    rect(x, y + h - 30, w, 30, DEEP)              # deep water band
    for i in range(9):                            # wave dashes
        rect(x + 24 + i * 62, y + h - 58, 30, 5, WHITE)
    # factory, left: chimneys, smoke, main hall
    for cx0 in (x + 62, x + 112, x + 162):
        rect(cx0, y + 44, 17, 52, INK)
        circle(cx0 + 8, y + 30, 10, GREY)
        circle(cx0 + 20, y + 20, 8, GREY)
    rect(x + 36, y + 96, 218, 52, GREY)
    rect(x + 36, y + 96, 218, 8, INK)
    for i in range(5):                            # factory windows
        rect(x + 54 + i * 40, y + 116, 20, 14, YELLOW)
    # container stacks on the quay, centre
    quay = y + h - 62
    for i, c in enumerate((RED, YELLOW, NAVY)):
        rect(x + 300 + i * 8, quay - 26, 118, 26, c)
        frame(x + 300 + i * 8, quay - 26, 118, 26, 2, INK)
    for i, c in enumerate((SAND, RED)):
        rect(x + 316 + i * 8, quay - 52, 102, 26, c)
        frame(x + 316 + i * 8, quay - 52, 102, 26, 2, INK)
    rect(x, quay, w, 6, INK)                      # quay edge
    # container ship, right
    rect(x + 560, y + 108, 320, 24, RED)
    rect(x + 560, y + 132, 320, 7, INK)
    for i, c in enumerate((NAVY, SAND, GREEN, YELLOW)):
        rect(x + 576 + i * 56, y + 84, 50, 24, c)
        frame(x + 576 + i * 56, y + 84, 50, 24, 2, INK)
    rect(x + 812, y + 62, 30, 46, WHITE)          # bridge tower
    rect(x + 819, y + 70, 16, 9, NAVY)
    # the tariff badge in the sky
    circle(x + w - 84, y + 58, 36, YELLOW)
    ring = 36
    for yy in range(y + 58 - ring, y + 58 + ring + 1):
        for xx in range(x + w - 84 - ring, x + w - 84 + ring + 1):
            d = (xx - (x + w - 84)) ** 2 + (yy - (y + 58)) ** 2
            if (ring - 4) ** 2 <= d <= ring ** 2:
                put(xx, yy, INK)
    draw_text(x + w - 84 - 22, y + 58 - 21, "%", 6, RED)


def refinery_icon(cx, y):
    """A drone over oil tanks at Samara; one tank burning. About 84 px."""
    # drone: body, arms, rotors
    rect(cx - 11, y - 2, 22, 7, RED)
    line(cx - 24, y - 8, cx + 24, y + 6, 3, INK)
    line(cx - 24, y + 6, cx + 24, y - 8, 3, INK)
    for dx in (-28, 28):
        rect(cx + dx - 8, y - 12, 16, 4, INK)
        rect(cx + dx - 8, y + 8, 16, 4, INK)
    # storage tanks, centred on cx
    for tx in (cx - 56, cx - 17, cx + 22):
        rect(tx, y + 34, 34, 42, GREY)
        circle(tx + 17, y + 34, 17, GREY)
        rect(tx, y + 52, 34, 4, INK)
    # flame and smoke on the middle tank
    circle(cx, y + 12, 11, FLAME)
    circle(cx, y + 6, 7, YELLOW)
    circle(cx + 11, y + 2, 8, GREY)
    rect(cx - 62, y + 78, 150, 4, INK)            # ground


def rocket_icon(cx, y):
    """Shenzhou-24: a rocket climbing to a small station. About 80 px."""
    # station, top right: truss and two solar wings
    rect(cx + 18, y + 7, 58, 5, GREY)
    rect(cx + 24, y + 0, 20, 18, NAVY)
    rect(cx + 52, y + 0, 20, 18, NAVY)
    circle(cx + 47, y + 9, 4, YELLOW)
    # rocket: stepped nose cone, body, window, fins, flame
    for i in range(5):
        half = 12 - i * 2
        rect(cx - half, y + 20 + i * 4, half * 2, 4, RED)
    rect(cx - 13, y + 40, 26, 28, WHITE)
    frame(cx - 13, y + 40, 26, 28, 2, INK)
    circle(cx, y + 50, 6, NAVY)                   # window
    rect(cx - 24, y + 56, 9, 12, RED)             # fins
    rect(cx + 15, y + 56, 9, 12, RED)
    circle(cx, y + 74, 6, FLAME)
    circle(cx, y + 71, 4, YELLOW)
    # stars
    for sx, sy in ((cx - 52, y + 8), (cx - 40, y + 30), (cx - 56, y + 52),
                   (cx + 30, y + 34), (cx - 30, y + 62)):
        rect(sx, sy, 4, 4, INK)


def boats_icon(cx, y):
    """Boats reaching a Canary island shore. About 84 px tall."""
    rect(cx - 62, y - 6, 124, 90, SEA)            # sea panel
    # island, left: stepped sand hill and a palm
    for i in range(4):
        rect(cx - 62, y + 52 - i * 8, 34 + i * 4, 8, SAND)
    line(cx - 40, y + 22, cx - 40, y + 2, 4, INK)
    line(cx - 40, y + 2, cx - 54, y - 4, 3, GREEN)
    line(cx - 40, y + 2, cx - 26, y - 4, 3, GREEN)
    line(cx - 40, y + 2, cx - 40, y - 8, 3, GREEN)
    # two boats with passengers
    for bx, by, n in ((cx - 2, y + 40, 4), (cx + 8, y + 62, 5)):
        rect(bx, by, 52, 10, RED)
        line(bx, by + 12, bx + 52, by + 12, 3, INK)
        for i in range(n):                        # heads and shoulders
            circle(bx + 8 + i * 10, by - 6, 4, INK)
            rect(bx + 5 + i * 10, by - 3, 7, 4, INK)
    for i in range(3):                            # wave dashes
        rect(cx - 52 + i * 36, y + 76, 16, 3, WHITE)


# ------------------------------------------------------------- page
def build():
    rect(0, 0, W, H, PAPER)
    frame(16, 16, W - 32, H - 32, 4, INK)
    frame(28, 28, W - 56, H - 56, 2, INK)

    # masthead
    centered(52, "THE WORLD IN ONE IMAGE", 4, NAVY, track=8)
    centered(96, "WEDNESDAY", 5, RED, track=14)
    centered(146, "25 NOVEMBER 2026", 10, INK)
    rect(64, 232, W - 128, 4, INK)
    rect(64, 242, W - 128, 2, INK)

    # lead story: US tariffs
    port_scene(64, 262, W - 128, 208)
    frame(64, 262, W - 128, 208, 3, INK)
    block(64, 490, "US PROPOSES NEW TARIFFS ON 14 PARTNERS", 6, INK,
          W - 128, leading=54, center=True)
    block(104, 612,
          "WASHINGTON CITES EXCESS FACTORY CAPACITY. CHINA FACES A NEW "
          "20% DUTY AND REJECTS THE CHARGE. ASIAN MARKETS SLID.",
          3, NAVY, W - 208, leading=28, center=True)

    rect(64, 700, W - 128, 3, INK)

    # three panels: icon band 720-796, headline 802-870, body 876-948
    cols = (64, 368, 672)
    for cx in cols:
        frame(cx, 712, 288, 232, 2, GREY)
    refinery_icon(cols[0] + 144, 722)
    rocket_icon(cols[1] + 144, 714)
    boats_icon(cols[2] + 144, 720)
    block(cols[0] + 12, 798, "DRONES HIT SAMARA", 4, INK, 264,
          leading=34, center=True)
    block(cols[0] + 12, 872,
          "UKRAINIAN DRONES STRUCK SAMARA REGION; ONE KILLED. "
          "REFINERY HITS UNVERIFIED.",
          2, NAVY, 264, leading=18, center=True)
    block(cols[1] + 12, 798, "SHENZHOU-24 DOCKS", 4, INK, 264,
          leading=34, center=True)
    block(cols[1] + 12, 872,
          "CHINA'S CREW REACHES TIANGONG WITH PAKISTAN'S FIRST "
          "ASTRONAUT ABOARD.",
          2, NAVY, 264, leading=18, center=True)
    block(cols[2] + 12, 798, "CANARY RECORD", 4, INK, 264,
          leading=34, center=True)
    block(cols[2] + 12, 872,
          "2,100 MIGRANTS REACHED SPAIN'S CANARY ISLANDS IN A DAY, A "
          "SINGLE-DAY RECORD.",
          2, NAVY, 264, leading=18, center=True)

    centered(954, "ALSO: RSF DRONES KILLED CIVILIANS IN SUDAN, A RIGHTS "
                  "GROUP SAYS; TOLL DISPUTED.", 2, INK, track=1)
    centered(976, "REPORTED BY REUTERS, AFP AND XINHUA", 2, GREY)


def main():
    build()
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        start = yy * W * 3
        raw += PX[start:start + W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
