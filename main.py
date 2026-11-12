import hashlib
import math
import os
import struct
import sys
import zlib

S = 2
W = H = 640
RW = RH = W * S
pixels = bytearray(RW * RH * 3)

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def blend(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))

def put(x, y, c):
    x, y = int(x), int(y)
    if 0 <= x < RW and 0 <= y < RH:
        p = (y * RW + x) * 3
        pixels[p:p + 3] = bytes(c)

def ellipse(cx, cy, rx, ry, color, outline=None, ow=1):
    cx, cy, rx, ry, ow = [v * S for v in (cx, cy, rx, ry, ow)]
    c = rgb(color) if isinstance(color, str) else color
    oc = rgb(outline) if isinstance(outline, str) else outline
    x0, x1 = max(0, int(cx-rx-ow)), min(RW, int(cx+rx+ow+1))
    y0, y1 = max(0, int(cy-ry-ow)), min(RH, int(cy+ry+ow+1))
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = ((x + .5-cx)/rx)**2 + ((y + .5-cy)/ry)**2
            if d <= 1:
                put(x, y, c)
            elif oc and ((x + .5-cx)/(rx+ow))**2 + ((y + .5-cy)/(ry+ow))**2 <= 1:
                put(x, y, oc)

def line(points, color, width=2):
    c = rgb(color) if isinstance(color, str) else color
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        dx, dy = bx-ax, by-ay
        n = max(1, int(math.hypot(dx, dy) * S * 1.5))
        for i in range(n + 1):
            t = i / n
            ellipse(ax+dx*t, ay+dy*t, width/2, width/2, c)

def polygon(points, color):
    c = rgb(color) if isinstance(color, str) else color
    pts = [(x*S, y*S) for x, y in points]
    for y in range(max(0, int(min(p[1] for p in pts))), min(RH, int(max(p[1] for p in pts))+1)):
        for x in range(max(0, int(min(p[0] for p in pts))), min(RW, int(max(p[0] for p in pts))+1)):
            inside = False
            j = len(pts)-1
            for i in range(len(pts)):
                xi, yi = pts[i]; xj, yj = pts[j]
                if ((yi > y) != (yj > y)) and x < (xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:
                    inside = not inside
                j = i
            if inside:
                put(x, y, c)

def flower(x, y, scale=1):
    for a in range(5):
        t = a * math.tau/5
        ellipse(x+math.cos(t)*3*scale, y+math.sin(t)*3*scale, 2.5*scale, 2.5*scale, "#FFFDF8")
    ellipse(x, y, 1.5*scale, 1.5*scale, "#F4C85C")

def star(x, y, r, color):
    line([(x-r,y),(x+r,y)], color, 1.2)
    line([(x,y-r),(x,y+r)], color, 1.2)
    ellipse(x,y,1,1,color)

def background():
    top, mid, bot = rgb("#FDF3E7"), rgb("#FDE8F0"), rgb("#DFF3E8")
    for y in range(RH):
        t = y/(RH-1)
        c = blend(top, mid, t*2) if t < .5 else blend(mid, bot, (t-.5)*2)
        for x in range(RW): put(x,y,c)
    ellipse(535, 105, 45, 45, "#FFF5D6")
    for x,y,r,c in [(90,90,7,"#FFFDF6"),(174,145,5,"#F7D992"),(432,72,7,"#FFFDF6"),(570,210,5,"#F7D992"),(290,105,4,"#FFFDF6"),(492,165,3,"#F7D992")]: star(x,y,r,c)
    for x,y,a in [(235,80,-.4),(382,125,.7),(585,120,-.2),(75,185,.3),(320,70,1)]:
        ellipse(x,y,3,5,"#F4B8C8")
        line([(x-2,y-3),(x+2,y+3)], "#F4B8C8", .7)
    ellipse(108,246,55,17,"#FFFAF6"); ellipse(150,240,31,24,"#FFFAF6"); ellipse(183,248,42,15,"#FFFAF6")
    ellipse(440,205,42,14,"#FFFAF6"); ellipse(473,199,27,21,"#FFFAF6"); ellipse(503,206,38,14,"#FFFAF6")
    ellipse(320,655,410,105,"#B9DDBA")
    for x,y in [(45,576),(100,603),(545,580),(590,610),(210,622),(430,615)]:
        line([(x,y+12),(x+1,y)],"#78B886",1.2); flower(x,y,1)

def scene():
    # A quiet pale halo frames the little pair.
    ring = [(320 + 171*math.cos(i*math.tau/180), 420 + 202*math.sin(i*math.tau/180)) for i in range(181)]
    line(ring, "#FFF9F5", 5)
    # fawn's feet and body
    ellipse(320, 498, 99, 92, "#C98B58")
    ellipse(278, 545, 31, 43, "#D39A67")
    ellipse(362, 545, 31, 43, "#D39A67")
    # ears, then the pink inner ear shapes
    ellipse(235, 261, 38, 83, "#BF8050")
    ellipse(405, 261, 38, 83, "#BF8050")
    ellipse(237, 263, 23, 61, "#EFA9A7")
    ellipse(403, 263, 23, 61, "#EFA9A7")
    # head
    ellipse(320, 356, 111, 107, "#D49A65")
    # forehead and cheek flecks
    for x,y,r in [(284,286,4),(307,278,3),(330,281,4),(350,290,3),(248,373,3),(256,389,2.5),(382,384,3),(391,369,2.5)]:
        ellipse(x,y,r,r,"#FFF2DC")
    # flower crown
    for x,y in [(273,274),(286,264),(302,256),(318,253),(334,256),(350,264),(363,275)]: flower(x,y,.9)
    # large glossy eyes
    for x in (282,358):
        ellipse(x, 351, 20, 24, "#4A3028")
        ellipse(x-6, 344, 7.5, 8.5, "#FFFFFF")
        ellipse(x+6, 356, 4.5, 5, "#FFFDF8")
    # muzzle, nose and gentle w mouth
    ellipse(320, 387, 24, 17, "#E8B58A")
    ellipse(320, 382, 6, 4, "#56352E")
    line([(320,386),(320,392),(315,396),(310,394)], "#56352E", 1.8)
    line([(320,392),(325,396),(330,394)], "#56352E", 1.8)
    ellipse(260, 393, 16, 10, "#E98991")
    ellipse(380, 393, 16, 10, "#E98991")
    # sage ribbon and bow at the neck
    ellipse(320, 462, 51, 16, "#91B99A")
    polygon([(315,458),(292,444),(295,467),(316,464)], "#83AA8D")
    polygon([(325,458),(348,444),(345,467),(324,464)], "#83AA8D")
    ellipse(320, 460, 7, 7, "#6F967C")
    # bunny ears sit behind its round body
    ellipse(301, 447, 17, 55, "#FFFCF8")
    ellipse(301, 447, 9, 42, "#F5B9C4")
    ellipse(371, 452, 18, 49, "#FFFCF8")
    ellipse(371, 452, 10, 35, "#F5B9C4")
    # fawn's reaching forelegs wrap around bunny
    ellipse(269, 478, 27, 55, "#D49A65")
    ellipse(373, 478, 27, 55, "#D49A65")
    # bunny, nestled at lower centre
    ellipse(322, 514, 49, 50, "#FFFEFB")
    ellipse(300, 548, 15, 10, "#F7C3C8")
    ellipse(344, 548, 15, 10, "#F7C3C8")
    # sleepy curved eyes
    line([(300,511),(305,515),(310,511)], "#8C7772", 1.7)
    line([(334,511),(339,515),(344,511)], "#8C7772", 1.7)
    ellipse(322, 520, 4, 3, "#E995A2")
    line([(322,522),(322,526),(318,528)], "#A27E7B", 1.2)
    line([(322,526),(326,528)], "#A27E7B", 1.2)
    # tiny flower tucked behind one bunny ear
    flower(282, 432, 1.15)

def downsample():
    out = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            p = ((y*2)*RW + x*2)*3
            q = ((y*2)*RW + x*2+1)*3
            r = p + RW*3
            t = r + 3
            o = (y*W+x)*3
            for k in range(3): out[o+k] = (pixels[p+k]+pixels[q+k]+pixels[r+k]+pixels[t+k]+2)//4
    return out

def chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)

def encode(data):
    scan = b"".join(b"\0" + data[y*W*3:(y+1)*W*3] for y in range(H))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W,H,8,2,0,0,0)) +
            chunk(b"IDAT", zlib.compress(scan, 9)) + chunk(b"IEND", b""))

def main():
    background()
    scene()
    data = encode(downsample())
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f: f.write(data)
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit("error: output is not a PNG")
    if W > 1024 or H > 1024:
        raise SystemExit("error: image dimensions exceed 1024")
    if len(data) > 1048576:
        raise SystemExit("error: PNG exceeds 1048576 bytes")
    print(f"Wrote {path} ({len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()})")

if __name__ == "__main__":
    main()
