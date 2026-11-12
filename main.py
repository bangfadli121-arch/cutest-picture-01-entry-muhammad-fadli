import hashlib
import math
import os
import struct
import sys
import zlib

W = H = 640
S = 2
SW = SH = W * S


def png_chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)


def save_png(path, pixels):
    rows = b"".join(b"\0" + bytes(pixels[y * SW * 3:(y + 1) * SW * 3]) for y in range(SH))
    data = b"\x89PNG\r\n\x1a\n"
    data += png_chunk(b"IHDR", struct.pack(">IIBBBBB", SW, SH, 8, 2, 0, 0, 0))
    data += png_chunk(b"IDAT", zlib.compress(rows, 9))
    data += png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def canvas():
    top, mid, bot = rgb("#FFE3EE"), rgb("#E6E0FF"), rgb("#D6F0FF")
    pix = bytearray(SW * SH * 3)
    for y in range(SH):
        t = y / (SH - 1)
        c = blend(top, mid, t * 2) if t < .5 else blend(mid, bot, (t - .5) * 2)
        start = y * SW * 3
        pix[start:start + SW * 3] = bytes(c) * SW
    return pix


def dot(pix, x, y, color):
    x, y = round(x * S), round(y * S)
    if 0 <= x < SW and 0 <= y < SH:
        i = (y * SW + x) * 3
        pix[i:i + 3] = bytes(color)


def ellipse(pix, x, y, rx, ry, color):
    x0, x1 = max(0, int((x - rx) * S)), min(SW, int((x + rx + 1) * S))
    y0, y1 = max(0, int((y - ry) * S)), min(SH, int((y + ry + 1) * S))
    cr = rgb(color) if isinstance(color, str) else color
    for py in range(y0, y1):
        dy = ((py / S) - y) / ry
        for px in range(x0, x1):
            dx = ((px / S) - x) / rx
            if dx * dx + dy * dy <= 1:
                i = (py * SW + px) * 3
                pix[i:i + 3] = bytes(cr)


def polygon(pix, points, color):
    cr = rgb(color) if isinstance(color, str) else color
    pts = [(x * S, y * S) for x, y in points]
    minx = max(0, int(min(x for x, y in pts)))
    maxx = min(SW - 1, int(max(x for x, y in pts)) + 1)
    miny = max(0, int(min(y for x, y in pts)))
    maxy = min(SH - 1, int(max(y for x, y in pts)) + 1)
    for py in range(miny, maxy + 1):
        for px in range(minx, maxx + 1):
            inside = False
            j = len(pts) - 1
            for i, (xi, yi) in enumerate(pts):
                xj, yj = pts[j]
                if ((yi > py) != (yj > py)) and px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi:
                    inside = not inside
                j = i
            if inside:
                k = (py * SW + px) * 3
                pix[k:k + 3] = bytes(cr)


def line(pix, points, color, width=2):
    r = width / 2
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        steps = max(1, int(math.hypot(x2 - x1, y2 - y1) * 3))
        for n in range(steps + 1):
            t = n / steps
            ellipse(pix, x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, r, r, color)


def heart(pix, x, y, s, color):
    ellipse(pix, x - s * .28, y, s * .34, s * .34, color)
    ellipse(pix, x + s * .28, y, s * .34, s * .34, color)
    polygon(pix, [(x - s * .58, y), (x + s * .58, y), (x, y + s * .72)], color)


def star(pix, x, y, r, color):
    polygon(pix, [(x, y-r), (x+r*.2, y-r*.2), (x+r, y), (x+r*.2, y+r*.2), (x, y+r), (x-r*.2, y+r*.2), (x-r, y), (x-r*.2, y-r*.2)], color)


def background(pix):
    ellipse(pix, 535, 105, 48, 48, "#FFF7D9")
    for x, y, r, c in [(75,95,8,"#FFF9E8"),(145,150,6,"#FFECA9"),(390,88,7,"#FFF9E8"),(470,185,6,"#FFECA9"),(95,220,5,"#FFF9E8"),(300,110,5,"#FFF9E8"),(575,245,6,"#FFF9E8")]:
        star(pix, x, y, r, c)
    heart(pix, 215, 95, 9, "#F7AFC5")
    heart(pix, 430, 145, 8, "#F7AFC5")
    heart(pix, 300, 205, 7, "#F7AFC5")
    heart(pix, 525, 220, 8, "#F7AFC5")
    for x, y in [(140,185),(175,185),(158,174),(390,230),(420,230),(405,218)]:
        ellipse(pix, x, y, 27, 15, "#FFFFFF")
    ellipse(pix, 157, 197, 45, 12, "#FFFFFF")
    ellipse(pix, 407, 242, 43, 12, "#FFFFFF")


def halo(pix):
    points = []
    for n in range(361):
        angle = math.radians(n)
        points.append((320 + 174 * math.cos(angle), 382 + 202 * math.sin(angle)))
    line(pix, points, "#FFFCF8", 7)
def panda(pix):
    # Mint hillside and simple blossoms
    ellipse(pix, 320, 647, 390, 105, "#BFE8D2")
    ellipse(pix, 110, 631, 95, 66, "#C9EEDB")
    ellipse(pix, 540, 625, 110, 75, "#C9EEDB")
    # Curling striped tail, layered from tip inward
    ellipse(pix, 465, 435, 96, 67, "#B94F35")
    ellipse(pix, 510, 403, 75, 65, "#D8754F")
    ellipse(pix, 528, 366, 58, 57, "#B94F35")
    ellipse(pix, 505, 344, 39, 40, "#D8754F")
    ellipse(pix, 484, 355, 22, 23, "#F8E8CC")
    ellipse(pix, 526, 389, 22, 38, "#F8E8CC")
    ellipse(pix, 487, 425, 22, 43, "#F8E8CC")
    # Small body and belly
    ellipse(pix, 320, 474, 88, 103, "#C95D3D")
    ellipse(pix, 320, 494, 51, 68, "#FFF1DC")
    # Ears with inner pink
    polygon(pix, [(233,237),(219,163),(282,203),(291,250)], "#B94F35")
    polygon(pix, [(249,219),(239,184),(272,207),(277,229)], "#F4A8A4")
    polygon(pix, [(347,250),(359,203),(421,163),(407,237)], "#B94F35")
    polygon(pix, [(361,228),(366,207),(400,184),(390,219)], "#F4A8A4")
    # Round cream face and crown patch
    ellipse(pix, 320, 306, 126, 112, "#FFF4E4")
    polygon(pix, [(272,218),(290,195),(320,214),(350,195),(368,219),(344,244),(320,235),(296,244)], "#C95D3D")
    # Eye patches and enormous glossy eyes
    ellipse(pix, 277, 307, 37, 44, "#A94733")
    ellipse(pix, 363, 307, 37, 44, "#A94733")
    ellipse(pix, 281, 307, 23, 28, "#302A34")
    ellipse(pix, 359, 307, 23, 28, "#302A34")
    ellipse(pix, 274, 298, 11, 12, "#FFFFFF")
    ellipse(pix, 286, 315, 5, 5, "#FFFFFF")
    ellipse(pix, 352, 298, 11, 12, "#FFFFFF")
    ellipse(pix, 364, 315, 5, 5, "#FFFFFF")
    # Muzzle, nose, smile, cheeks, whisker freckles
    ellipse(pix, 320, 342, 29, 20, "#FFF9EF")
    polygon(pix, [(309,333),(331,333),(320,346)], "#8F3D32")
    line(pix, [(320,346),(320,353),(313,359),(307,356)], "#54353A", 2.5)
    line(pix, [(320,353),(327,359),(333,356)], "#54353A", 2.5)
    ellipse(pix, 249, 348, 16, 9, "#F28F91")
    ellipse(pix, 391, 348, 16, 9, "#F28F91")
    for x, y in [(267,337),(270,347),(373,337),(370,347)]:
        ellipse(pix, x, y, 1.7, 1.7, "#9B6659")
    # Paws resting at the bottom
    ellipse(pix, 274, 555, 29, 18, "#FFF1DC")
    ellipse(pix, 366, 555, 29, 18, "#FFF1DC")
    # Three tiny flower heads in the grass
    for x, y in [(125,590),(430,602),(555,570)]:
        line(pix, [(x,y+10),(x,y+26)], "#76B78F", 2)
        for dx, dy in [(-5,0),(5,0),(0,-5),(0,5)]:
            ellipse(pix, x+dx, y+dy, 3.5, 3.5, "#FFF4DA")
        ellipse(pix, x, y, 2.5, 2.5, "#F3C763")


def downsample(pix):
    out = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            a = ((y * 2) * SW + x * 2) * 3
            b, c, d = a + 3, a + SW * 3, a + SW * 3 + 3
            o = (y * W + x) * 3
            for k in range(3):
                out[o+k] = (pix[a+k] + pix[b+k] + pix[c+k] + pix[d+k] + 2) // 4
    return out


def main():
    pix = canvas()
    background(pix)
    halo(pix)
    panda(pix)
    small = downsample(pix)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    # PNG encoder dimensions follow the required final 640 px canvas.
    global SW, SH
    old_sw, old_sh = SW, SH
    SW, SH = W, H
    save_png(path, small)
    SW, SH = old_sw, old_sh
    with open(path, "rb") as f:
        data = f.read()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit("error: output does not have a PNG signature")
    width, height = struct.unpack(">II", data[16:24])
    if width > 1024 or height > 1024:
        raise SystemExit("error: PNG dimensions exceed 1024")
    if len(data) > 1048576:
        raise SystemExit("error: PNG exceeds 1048576 bytes")
    print(f"Wrote {path} ({len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()})")


if __name__ == "__main__":
    main()
