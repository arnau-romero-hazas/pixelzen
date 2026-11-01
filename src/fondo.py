#!/usr/bin/env python3
"""PixelZen v2 - fondo + vista previa de widgets. Python puro (sin dependencias).
Lienzo 384x240, escalado x5 = 1920x1200 (en logico 1536x960: x4).
Uso: fondo.py <carpeta_salida>"""
import json, math, os, random, struct, sys, zlib

W, H, S = 384, 240, 5
random.seed(7)

def hx(c):
    if isinstance(c, tuple): return c
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
def mix(a, b, t):
    a, b = hx(a), hx(b); return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

px = [[(0, 0, 0)] * W for _ in range(H)]
def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: px[y][x] = hx(c)

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(x, y, t): return (BAYER[y % 4][x % 4] + 0.5) / 16 < t
def disc(cx, cy, r, c, plot=put):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r + r // 2: plot(cx + x, cy + y, c)

# zona reservada para widgets (cuadricula): columna derecha despejada
ZX0, ZX1, ZY0, ZY1 = 288, 380, 6, 130
def en_zona(x, y): return ZX0 - 4 <= x <= ZX1 + 4 and ZY0 - 4 <= y <= ZY1 + 4

# ---------- cielo ----------
SKY = ['#080a1a', '#0e1130', '#171a42', '#252357', '#3b2d68', '#5b3a73',
       '#8a4a79', '#b95e7c', '#e0837f', '#f2ab8c']
HOR = 168
for y in range(HOR):
    t = (y / HOR) ** 1.35 * (len(SKY) - 1); i = int(t); f = t - i
    for x in range(W):
        put(x, y, SKY[min(i + 1, len(SKY) - 1)] if dith(x, y, f) else SKY[i])

# ---------- estrellas (mas escasas en la zona de widgets) ----------
for _ in range(150):
    x, y = random.randrange(W), random.randrange(int(HOR * 0.55))
    if en_zona(x, y) and random.random() < 0.8: continue
    put(x, y, random.choice(['#f6efe0', '#cfd3ff', '#9aa0d8', '#6f74b0']))
    if random.random() < 0.07 and not en_zona(x, y):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(x + dx, y + dy, '#8f95d0')

# ---------- luna (centro, entera sobre las montañas) ----------
MX, MY, MR = 212, 50, 27
for y in range(MY - 70, MY + 70):
    for x in range(MX - 70, MX + 70):
        d = math.hypot(x - MX, y - MY)
        if MR < d < 64 and 0 <= y < HOR and dith(x, y, ((64 - d) / (64 - MR)) ** 2.2 * 0.38):
            put(x, y, '#c9a6c4')
for y in range(MY - MR, MY + MR + 1):
    for x in range(MX - MR, MX + MR + 1):
        if math.hypot(x - MX, y - MY) <= MR:
            c = '#f6ecd4'
            if math.hypot(x - (MX + 7), y - (MY + 6)) > MR - 9 and dith(x, y, 0.55): c = '#e2d4b6'
            put(x, y, c)
for cx, cy, r in ((-9, -8, 5), (6, -12, 3), (10, 9, 6), (-12, 8, 3), (-2, 14, 2)):
    disc(MX + cx, MY + cy, r, '#e4d6b8')

# ---------- nubes finas (una cruza la luna) ----------
def nube(cx, cy, w, col):
    for k in range(3):
        ww = w - k * 14
        for x in range(cx - ww // 2, cx + ww // 2):
            if dith(x, cy + k * 2, 0.85 - k * 0.2): put(x, cy + k * 2, col)
nube(96, 38, 110, '#4b3f7c'); nube(228, 100, 96, '#8a6aa0'); nube(60, 104, 120, '#9b5580')
nube(160, 132, 100, '#d77c82')

# ---------- montañas (bajan a la derecha para dejar sitio a los widgets) ----------
def rampa(x): return 1.0 if x < 250 else max(0.3, 1.0 - (x - 250) / 60 * 0.7)
def cresta(base, amp, seed, f1, f2):
    r = random.Random(seed); p1, p2, p3 = r.random() * 9, r.random() * 9, r.random() * 9
    return [base - amp * rampa(x) * (0.55 * math.sin(x * f1 + p1) + 0.3 * math.sin(x * f2 + p2)
                                     + 0.15 * math.sin(x * 0.19 + p3) + 0.5) for x in range(W)]
CAPAS = [(140, 46, 1, 0.021, 0.047, '#4a3a73', '#b8708a'), (150, 40, 2, 0.026, 0.061, '#352c60', '#8d5a85'),
         (158, 34, 3, 0.031, 0.073, '#262250', '#5e4580'), (166, 26, 4, 0.039, 0.089, '#171637', '#3a3068')]
for base, amp, seed, f1, f2, col, mist in CAPAS:
    c = cresta(base, amp, seed, f1, f2)
    for x in range(W):
        top = int(c[x])
        for y in range(top, HOR + 1): put(x, y, col)
        for k in range(1, 15):
            if dith(x, top + k, (1 - k / 15) * 0.55): put(x, top + k, mist)
    if seed == 4:
        for x in range(0, W, 3):
            if random.random() < 0.7:
                t0 = int(c[x]); h = random.randint(4, 9)
                for k in range(h):
                    for dx in range(-(k // 3), k // 3 + 1): put(x + dx, t0 - h + k + 1, '#0e0d26')

# ---------- isla con pagoda ----------
IX, IY = 128, HOR
for y in range(IY - 16, IY + 1):
    ww = int(46 * (1 - ((IY - y) / 16) ** 1.6)) if y < IY else 46
    for x in range(IX - ww // 2 - 8, IX + ww // 2 + 8): put(x, y, '#0b0a1e')
INK, INK2, WARM = '#07061a', '#14122e', '#f0b86e'
def techo(cx, y, w, h):
    for i in range(h):
        ww = w - i * 2
        for x in range(cx - ww // 2, cx + ww // 2 + 1): put(x, y + i, INK)
    for k in range(4):
        put(cx - w // 2 - k, y - (k + 1) // 2 + 1, INK); put(cx + w // 2 + k, y - (k + 1) // 2 + 1, INK)
def piso(cx, y, w, h):
    for yy in range(y, y + h):
        for x in range(cx - w // 2, cx + w // 2 + 1): put(x, yy, INK2)
    for k in range(-w // 2 + 3, w // 2 - 2, 4): put(cx + k, y + 2, WARM); put(cx + k, y + 3, WARM)
by0 = IY - 14
piso(IX, by0 - 6, 24, 6);  techo(IX, by0 - 9, 36, 4)
piso(IX, by0 - 16, 20, 6); techo(IX, by0 - 19, 30, 4)
piso(IX, by0 - 26, 16, 6); techo(IX, by0 - 29, 24, 4)
piso(IX, by0 - 36, 12, 6); techo(IX, by0 - 39, 18, 3)
for k in range(11): put(IX, by0 - 40 - k, INK)
put(IX, by0 - 52, '#c8382e')

# ---------- lago (reflejo del paisaje, sin el torii) ----------
copia = [list(r) for r in px[:HOR + 1]]
for y in range(HOR + 1, H):
    d = y - HOR; src = HOR - 1 - int(d * 1.15)
    ondas = int(2 * math.sin(d * 0.9))
    for x in range(W):
        sx = (x + ondas + (2 if (d // 3) % 2 else -2)) % W
        k = max(0.18, 0.62 - d * 0.006)
        put(x, y, mix('#0a0c24', copia[max(src, 0)][sx], k))
for y in range(HOR + 2, H, 3):
    for _ in range(14):
        x = random.randrange(W); l = random.randint(3, 14)
        c = '#a47aa0' if y < HOR + 22 else '#3c3a6a'
        for k in range(l): put(x + k, y, c)
for d in range(6, 70, 3):                      # camino de la luna en el agua
    ww = int(22 - d * 0.24)
    for x in range(MX - ww // 2, MX + ww // 2):
        if random.random() < 0.55: put(x, HOR + d, '#f1dfc2' if d < 30 else '#c9a6c4')

# ---------- torii con base de piedra y reflejo limpio ----------
TX, TBY = 262, 196
def torii(cx, by, plot):
    R, R2 = '#c8382e', '#8a2420'; h, sep = 34, 30
    for dx in (-sep // 2, sep // 2):
        for y in range(by - h, by):
            for t in range(-2, 3): plot(cx + dx + t, y, R if t >= 0 else R2)
    for y in range(by - h - 2, by - h + 3):
        for x in range(cx - sep // 2 - 12, cx + sep // 2 + 13): plot(x, y, R)
    for k in range(5):
        plot(cx - sep // 2 - 12 - k, by - h - 2 - (k + 1) // 2, R); plot(cx + sep // 2 + 12 + k, by - h - 2 - (k + 1) // 2, R)
    for y in range(by - h + 3, by - h + 6):
        for x in range(cx - sep // 2 - 10, cx + sep // 2 + 11): plot(x, y, R2)
    for y in range(by - h + 10, by - h + 14):
        for x in range(cx - sep // 2 - 3, cx + sep // 2 + 4): plot(x, y, R)
    for y in range(by - h - 2, by - h + 3): plot(cx, y, R2)
mask = {}
torii(TX, TBY, lambda x, y, c: mask.__setitem__((x, y), hx(c)))
for dy in range(0, 46):                         # reflejo: espejo + ondas + se apaga
    if dy % 4 == 3: continue
    sh = 1 if (dy // 2) % 2 else -1
    a = min(0.62, 0.5 - dy * 0.006 + 0.1)
    for (x, y), c in mask.items():
        if y == TBY - 1 - dy:
            for xx in (x + sh,): put(xx, TBY + dy, mix(px[TBY + dy][xx] if 0 <= xx < W else '#0a0c24', mix(c, '#2a1840', 0.4), a))
for dx in (-15, 15):                     # piedras de la base + anillos de agua
    for y in range(TBY - 3, TBY + 1):
        for x in range(TX + dx - 5, TX + dx + 6): put(x, y, '#4a3f78' if y == TBY - 3 else '#2c2652')
    for x in range(TX + dx - 9, TX + dx + 10):
        if abs(x - (TX + dx)) > 5 and dith(x, TBY + 1, 0.6): put(x, TBY + 1, '#b497b8')
torii(TX, TBY - 3, put)

# ---------- cerezo: rama con tronco que se afina y racimos de flor ----------
RAMA = '#120a19'
def rama(pts, r0, r1):
    n = sum(max(abs(b[0] - a[0]), abs(b[1] - a[1])) for a, b in zip(pts, pts[1:])) or 1; i = 0
    for a, b in zip(pts, pts[1:]):
        m = max(abs(b[0] - a[0]), abs(b[1] - a[1])) or 1
        for k in range(m + 1):
            r = r0 + (r1 - r0) * (i / n); i += 1
            disc(a[0] + (b[0] - a[0]) * k // m, a[1] + (b[1] - a[1]) * k // m, max(1, round(r)), RAMA)
        i -= 1
rama([(-6, 16), (14, 22), (38, 30), (62, 34), (88, 34), (112, 42), (142, 42)], 4, 1)
rama([(38, 30), (46, 52), (54, 66), (46, 90)], 3, 1)
rama([(88, 34), (100, 16), (122, 8)], 2, 1)
rama([(112, 42), (120, 62), (128, 76)], 2, 1)
rama([(14, 22), (22, 8), (26, 0)], 2, 1)
ROSA_L, ROSA, ROSA_M, ROSA_D = '#fbe9ee', '#f2b8c6', '#e48fa8', '#c4688a'
def racimo(cx, cy, R):
    R = max(6, int(R * 0.58))
    cells = {}
    for _ in range(R + 3):
        ox, oy = random.randint(-R // 2, R // 2), random.randint(-R // 2, R // 2)
        disc(cx + ox, cy + oy, random.randint(2, max(3, R // 2)), 1, lambda x, y, c: cells.__setitem__((x, y), 1))
    for (x, y) in cells:
        v = ((x - cx) + (y - cy)) / (2.0 * R)
        c = ROSA
        if v > 0.15: c = ROSA_D if (v > 0.55 and dith(x, y, 0.6)) or (v > 0.4 and dith(x, y, 0.2)) else ROSA_M
        elif v < -0.3: c = ROSA_L if dith(x, y, min(1, -v * 1.2)) else ROSA
        if (x, y) in cells and (x + 1, y) not in cells: c = ROSA_D if v > 0 else ROSA_M   # contorno
        put(x, y, c)
    for _ in range(R // 2):
        x, y = cx + random.randint(-R // 2, R // 2), cy + random.randint(-R // 2, R // 2)
        if (x, y) in cells: put(x, y, '#f6c76b' if random.random() < 0.3 else ROSA_L)
    for _ in range(4):                                         # petalos sueltos alrededor
        a = random.random() * 6.28; rr = R * 0.8 + random.random() * 6
        put(int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr), random.choice((ROSA, ROSA_M)))
for cx, cy, R in ((8, 18, 16), (34, 28, 15), (60, 36, 16), (86, 32, 17), (100, 20, 12), (124, 10, 13),
                  (110, 44, 15), (138, 42, 11), (24, 24, 12), (72, 34, 12), (96, 36, 12), (126, 44, 12), (50, 48, 10), (52, 70, 10), (118, 56, 9), (100, 14, 9), (10, 6, 9), (44, 58, 14), (48, 84, 12), (122, 68, 11), (22, 4, 10)):
    racimo(cx, cy, R)
for _ in range(26):                                            # petalos al viento
    x, y = random.randrange(W), random.randrange(0, 205)
    if en_zona(x, y): continue
    put(x, y, random.choice((ROSA, ROSA_M))); put(x + 1, y + 1, ROSA_L)

# ---------- vineta ----------
for y in range(H):
    for x in range(W):
        d = math.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2))
        if d > 0.85 and dith(x, y, (d - 0.85) * 0.9):
            r, g, b = px[y][x]; px[y][x] = (int(r * 0.72), int(g * 0.72), int(b * 0.78))

# ---------- PNG ----------
def png(ruta, buf):
    raw = bytearray()
    for y in range(H):
        fila = b''.join(bytes(buf[y][x]) * S for x in range(W)); raw += (b'\x00' + fila) * S
    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(ruta, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W * S, H * S, 8, 2, 0, 0, 0))
                + ch(b'IDAT', zlib.compress(bytes(raw), 9)) + ch(b'IEND', b''))

out = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(out, exist_ok=True)
png(os.path.join(out, 'v2.png'), px)

# ========== vista previa de widgets (maqueta con fuente 3x5) ==========
F = {'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
     'E': '111100110100111', 'F': '111100110100100', 'G': '011100101101011', 'H': '101101111101101',
     'I': '111010010010111', 'K': '101101110101101', 'L': '100100100100111', 'M': '101111111101101',
     'N': '110101101101101', 'O': '010101101101010', 'P': '110101110100100', 'R': '110101110101101',
     'S': '011100010001110', 'T': '111010010010010', 'U': '101101101101111', 'V': '101101101101010',
     'W': '101101111111101', 'X': '101101010101101', 'Y': '101101010010010', 'N2': '',
     '0': '111101101101111', '1': '010110010010111', '2': '110001010100111', '3': '110001010001110',
     '4': '101101111001001', '5': '111100110001110', '6': '011100111101111', '7': '111001010010010',
     '8': '111101111101111', '9': '111101111001110', ':': '000010000010000', '.': '000000000000010',
     '%': '101001010100101', '-': '000000111000000', '+': '000010111010000', ' ': '000000000000000'}
def texto(buf, x, y, s, col, esc=1):
    for ch in s.upper():
        g = F.get(ch, F[' '])
        for i, bit in enumerate(g):
            if bit == '1':
                for a in range(esc):
                    for b in range(esc):
                        xx, yy = x + (i % 3) * esc + a, y + (i // 3) * esc + b
                        if 0 <= xx < W and 0 <= yy < H: buf[yy][xx] = hx(col)
        x += 4 * esc
def rect(buf, x0, y0, x1, y1, col, a=1.0):
    for y in range(y0, y1):
        for x in range(x0, x1):
            if 0 <= x < W and 0 <= y < H: buf[y][x] = mix(buf[y][x], col, a)
def panel(buf, x0, y0, x1, y1):
    rect(buf, x0, y0, x1, y1, '#0a0c24', 0.74)
    rect(buf, x0, y0, x1, y0 + 1, '#6a4a8a'); rect(buf, x0, y1 - 1, x1, y1, '#6a4a8a')
    rect(buf, x0, y0, x0 + 1, y1, '#6a4a8a'); rect(buf, x1 - 1, y0, x1, y1, '#6a4a8a')
    rect(buf, x0, y0, x0 + 4, y0 + 1, '#c8382e'); rect(buf, x0, y0, x0 + 1, y0 + 4, '#c8382e')   # esquina torii
WASHI, LAB = '#f3e9d2', '#b8708a'
pv = [list(r) for r in px]
X0, X1 = 292, 378
panel(pv, X0, 8, X1, 40)                                                  # reloj
texto(pv, X0 + 8, 13, '14:32', WASHI, 3); texto(pv, X0 + 8, 32, 'DOM 01 NOV', LAB)
rect(pv, X1 - 14, 12, X1 - 7, 19, '#c8382e')                              # hanko
panel(pv, X0, 44, X1, 84)                                                 # sistema
for i, (n, v, c) in enumerate((('CPU', 23, '#c8382e'), ('RAM', 41, '#e0b36a'), ('TMP', 52, '#7fb88a'))):
    yy = 50 + i * 10; texto(pv, X0 + 6, yy, n, LAB)
    rect(pv, X0 + 26, yy + 1, X0 + 64, yy + 4, '#2b2850'); rect(pv, X0 + 26, yy + 1, X0 + 26 + 38 * v // 100, yy + 4, c)
    texto(pv, X0 + 68, yy, f'{v}%', WASHI)
panel(pv, X0, 88, X1, 126)                                                # red + dev
for i, (a, b) in enumerate((('NET', 'WLAN0 UP'), ('VPN', 'OFF'), ('GIT', 'MAIN +3'), ('DKR', '2 UP'))):
    yy = 94 + i * 8; texto(pv, X0 + 6, yy, a, LAB); texto(pv, X0 + 30 if a != 'DOCKER' else X0 + 30, yy, b, WASHI)
png(os.path.join(out, 'v2-preview.png'), pv)

# zonas para colocar los widgets reales (px fisicos 1920x1200 y logicos 1536x960)
zonas = {'cuadricula': [W, H], 'zona_widgets': {'x': [ZX0, ZX1], 'y': [ZY0, ZY1]},
         'paneles_fisicos': {'reloj': [X0 * S, 8 * S, X1 * S, 40 * S], 'sistema': [X0 * S, 44 * S, X1 * S, 84 * S],
                             'red_dev': [X0 * S, 88 * S, X1 * S, 126 * S]},
         'paneles_logicos': {'reloj': [X0 * 4, 32, X1 * 4, 160], 'sistema': [X0 * 4, 176, X1 * 4, 336],
                             'red_dev': [X0 * 4, 352, X1 * 4, 504]}}
json.dump(zonas, open(os.path.join(out, 'zonas.json'), 'w'), indent=2)
print('ok')
