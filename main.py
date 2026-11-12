import hashlib
import math
import os
import struct
import sys
import zlib

S = 2
W = H = 640
SW = SH = W * S
pixels = bytearray(SW * SH * 3)


def paint(x, y, color):
    if 0 <= x < SW and 0 <= y < SH:
        i = (y * SW + x) * 3
        pixels[i:i + 3] = bytes(color)


def ellipse(cx, cy, rx, ry, color):
    x0, x1 = max(0, int(cx-rx)), min(SW-1, int(cx+rx))
    y0, y1 = max(0, int(cy-ry)), min(SH-1, int(cy+ry))
    for y in range(y0, y1+1):
        dy = (y-cy)/ry
        for x in range(x0, x1+1):
            dx = (x-cx)/rx
            if dx*dx + dy*dy <= 1:
                paint(x, y, color)


def polygon(points, color):
    pts = [(int(x), int(y)) for x, y in points]
    ymin, ymax = max(0, min(y for _, y in pts)), min(SH-1, max(y for _, y in pts))
    for y in range(ymin, ymax+1):
        xs = []
        for i, (x1, y1) in enumerate(pts):
            x2, y2 = pts[(i+1) % len(pts)]
            if y1 != y2 and min(y1, y2) <= y < max(y1, y2):
                xs.append(x1 + (y-y1)*(x2-x1)/(y2-y1))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(max(0, int(a)), min(SW, int(b)+1)):
                paint(x, y, color)


def line(x1, y1, x2, y2, color, width=2):
    steps = max(1, int(math.hypot(x2-x1, y2-y1)))
    for n in range(steps+1):
        t = n/steps
        ellipse(x1+(x2-x1)*t, y1+(y2-y1)*t, width/2, width/2, color)


def C(x, y):
    return (x*S, y*S)


def circle(x, y, r, color):
    ellipse(x*S, y*S, r*S, r*S, color)


def oval(x, y, rx, ry, color):
    ellipse(x*S, y*S, rx*S, ry*S, color)


def poly(points, color):
    polygon([C(x, y) for x, y in points], color)


def stroke(points, color, width=2):
    for a, b in zip(points, points[1:]):
        line(*C(*a), *C(*b), color, width*S)


def background():
    top, mid, bot = (255,246,229), (255,233,243), (223,243,255)
    for y in range(SH):
        yy = y/S
        if yy < 320:
            t=yy/320; a,b=top,mid
        else:
            t=(yy-320)/320; a,b=mid,bot
        col=tuple(round(a[k]*(1-t)+b[k]*t) for k in range(3))
        pixels[y*SW*3:(y+1)*SW*3]=bytes(col)*SW
    circle(548, 91, 43, (255,250,220))
    for x,y,r in [(82,86,4),(154,145,3),(461,75,3),(570,192,4),(97,235,3),(500,235,3),(206,69,3)]:
        poly([(x,y-r*2),(x+1,y-1),(x+r*2,y),(x+1,y+1),(x,y+r*2),(x-1,y+1),(x-r*2,y),(x-1,y-1)], (255,255,245))
    for x,y in [(125,190),(442,157),(535,283),(72,293)]:
        circle(x-5,y,4,(255,190,211)); circle(x,y-4,4,(255,190,211)); circle(x+5,y,4,(255,190,211)); circle(x,y+4,4,(255,190,211)); circle(x,y,3,(255,237,184))
    for x,y in [(91,362),(490,355)]:
        oval(x,y+9,43,18,(255,255,255)); circle(x-25,y,15,(255,255,255)); circle(x,y-8,21,(255,255,255)); circle(x+24,y,15,(255,255,255))
    oval(320, 646, 370, 103, (196,232,204))
    oval(320, 659, 370, 70, (177,222,190))
    for x,y in [(55,566),(113,606),(522,580),(582,615),(195,590),(453,625)]:
        for dx,dy in [(0,-5),(5,0),(0,5),(-5,0)]: circle(x+dx,y+dy,3,(255,255,245))
        circle(x,y,2,(255,213,112))

def vignette_ring():
    # A delicate white halo just outside the character silhouette.
    cx, cy, rx, ry = 320*S, 356*S, 184*S, 224*S
    for y in range(max(0, cy-ry-2*S), min(SH, cy+ry+2*S)):
        for x in range(max(0, cx-rx-2*S), min(SW, cx+rx+2*S)):
            d=((x-cx)/rx)**2+((y-cy)/ry)**2
            if 0.965 <= d <= 1.045:
                i=(y*SW+x)*3
                for c in range(3): pixels[i+c]=(pixels[i+c]*3+255)//4


def kitten_and_chick():
    ink=(92,75,85); fur=(255,252,241); shadow=(238,226,210)
    # Floating kitten body and ears
    oval(320, 448, 107, 119, shadow)
    oval(320, 441, 105, 117, fur)
    poly([(238,176),(248,76),(310,148)], shadow)
    poly([(242,165),(253,91),(298,151)], (255,198,207))
    poly([(336,148),(394,76),(403,178)], shadow)
    poly([(349,148),(391,95),(395,164)], (255,198,207))
    # Crown daisies
    for x,y in [(266,126),(286,112),(308,106),(331,106),(352,112),(371,126)]:
        for dx,dy in [(0,-8),(7,-3),(5,5),(-5,5),(-7,-3)]: circle(x+dx,y+dy,5,(255,255,255))
        circle(x,y,4,(255,212,103))
    # Head
    oval(320, 251, 114, 103, shadow)
    oval(320, 244, 112, 102, fur)
    # Eyes with soft blue irises and white glints
    for x in (278,362):
        oval(x,249,23,28,(100,177,219))
        oval(x,251,15,20,(44,69,91))
        circle(x-7,241,9,(255,255,255)); circle(x+7,258,4,(255,255,255))
    # Cheeks, nose and little w mouth
    oval(248,282,18,10,(255,174,168)); oval(392,282,18,10,(255,174,168))
    poly([(320,271),(313,277),(327,277)],(242,139,157))
    stroke([(320,278),(320,285),(311,291),(304,287)],ink,2)
    stroke([(320,285),(329,291),(336,287)],ink,2)
    for x,y in [(243,267),(250,271),(397,267),(390,271)]: circle(x,y,2,ink)
    # Mint scarf around neck and knot
    poly([(248,342),(392,342),(376,374),(262,374)],(153,216,188))
    poly([(365,354),(403,363),(385,394),(368,380)],(130,201,175))
    poly([(378,370),(400,382),(384,422),(367,391)],(153,216,188))
    # Paws reaching around chick
    oval(266,445,49,34,fur); oval(374,445,49,34,fur)
    oval(265,449,35,25,(255,231,218)); oval(375,449,35,25,(255,231,218))
    # Chick body nestled in paws
    oval(320,453,48,49,(255,213,102))
    oval(320,450,43,44,(255,224,126))
    # Three feathers
    for x,y in [(307,405),(320,400),(333,405)]: oval(x,y,5,10,(255,213,102))
    # sleepy bright eyes and beak
    for x in (305,335):
        oval(x,447,4,5,(74,66,66)); circle(x-1,445,1.8,(255,255,255))
    poly([(320,454),(312,461),(328,461)],(239,143,70))
    oval(305,498,9,4,(255,166,120)); oval(335,498,9,4,(255,166,120))
    # Tiny feather strokes and paw details
    stroke([(312,468),(315,470)],(245,184,91),1)
    stroke([(328,468),(331,470)],(245,184,91),1)
    for x in (254,378):
        stroke([(x-8,450),(x-3,453)],(224,183,165),1)
        stroke([(x+1,450),(x+6,453)],(224,183,165),1)


def png_chunk(kind, data):
    body=kind+data
    return struct.pack('>I',len(data))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)


def render_rgb():
    # Box-average each 2x2 block from the supersampled canvas.
    out=bytearray(W*H*3)
    for y in range(H):
        for x in range(W):
            dst=(y*W+x)*3
            src=((y*2)*SW+x*2)*3
            for c in range(3):
                out[dst+c]=(pixels[src+c]+pixels[src+3+c]+pixels[src+SW*3+c]+pixels[src+SW*3+3+c]+2)//4
    return out


def main():
    background()
    vignette_ring()
    kitten_and_chick()
    rgb=render_rgb()
    scanlines=b''.join(b'\0'+rgb[y*W*3:(y+1)*W*3] for y in range(H))
    data=(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+
          png_chunk(b'IDAT',zlib.compress(scanlines,9))+png_chunk(b'IEND',b''))
    outdir=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
    os.makedirs(outdir,exist_ok=True)
    path=os.path.join(outdir,'entry.png')
    with open(path,'wb') as f: f.write(data)
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise SystemExit('ERROR: output is missing the PNG signature')
    if W>1024 or H>1024:
        raise SystemExit('ERROR: output dimensions exceed 1024 pixels')
    if len(data)>1048576:
        raise SystemExit('ERROR: PNG exceeds 1048576 bytes')
    print(f'Wrote {path} ({len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()})')


if __name__=='__main__':
    main()
