#!/usr/bin/env python3
"""PixelZen v3 - fondo de alto detalle. Python puro (sin dependencias).
Lienzo 640x400, escalado x3 = 1920x1200 (en logico 1536x960: x2.4).
Uso: fondo3.py <carpeta_salida>"""
import json, math, os, random, struct, sys, zlib

W, H, S = 640, 400, 3
ANIM = '--anim' in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ESTRELLAS, VENTANAS, FAROLES, DESTELLOS, NUBES = [], [], [], [], []
random.seed(11)

def hx(c):
    if isinstance(c, tuple): return c
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
def mix(a, b, t):
    a, b = hx(a), hx(b); return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

px = [[(0, 0, 0)] * W for _ in range(H)]
def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: px[y][x] = hx(c)
def over(x, y, c, a):
    if 0 <= x < W and 0 <= y < H: px[y][x] = mix(px[y][x], c, a)
def get(x, y): return px[y][x] if 0 <= x < W and 0 <= y < H else (0, 0, 0)

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(x, y, t): return (BAYER[y % 4][x % 4] + 0.5) / 16 < t
def disc(cx, cy, r, c, plot=put):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r + r // 2: plot(cx + x, cy + y, c)
def glow(cx, cy, r, c, fuerza=0.7):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            d = math.hypot(x, y)
            if d < r and dith(cx + x, cy + y, ((1 - d / r) ** 2) * fuerza): over(cx + x, cy + y, c, 0.75)

class Ruido:
    def __init__(s, seed, n=96): r = random.Random(seed); s.v = [r.random() for _ in range(n)]
    def __call__(s, x):
        i = int(x); f = x - i; f = f * f * (3 - 2 * f)
        a, b = s.v[i % len(s.v)], s.v[(i + 1) % len(s.v)]; return a + (b - a) * f
def fbm(r, x): return 0.55 * r(x) + 0.28 * r(x * 2.1 + 7) + 0.17 * r(x * 4.3 + 3)

# zona reservada para widgets (columna derecha despejada)
ZX0, ZX1, ZY0, ZY1 = 478, 632, 10, 215
def en_zona(x, y, m=6): return ZX0 - m <= x <= ZX1 + m and ZY0 - m <= y <= ZY1 + m

HOR = 280                                  # linea del horizonte; el lago esta debajo

FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
PALETAS = {
 'noche': dict(
   sky=['#06081a', '#0a0d28', '#10143a', '#191c4a', '#252459', '#352c68', '#4a3578', '#63407c', '#85497d', '#a85a7e', '#cc7280', '#e8967f', '#f5b58f'],
   mont=['#4a3a73', '#3a3066', '#2a2554', '#1b1a3e', '#0f0e2a'], mist=['#c07890', '#a2628c', '#6e4e8a', '#43387a', '#2c2660'],
   nieve=('#eadcf0', '#b9a4d4'), filo='#e6c4e0', pino1='#090820', pino2='#12112e', pinorim='#2a2552',
   isla=('#0a091f', '#14122e', '#2a2552'), ink=('#06051a', '#12102c', '#1e1a42'), techo_luz='#4a3f84', bruma='#7a6aa8', agua='#080a22',
   ola=('#b08ab0', '#5a4a8a', '#34306a'), cana=('#05061a', '#1c1b44', '#07071e', '#252048'), vig=0.70, boat='#07061a', tor_ref='#2a1840',
   nube=['#5d4d92', '#8f70a8', '#a35c86', '#da8084', '#e59088', '#4e4488']),
 'dorado': dict(
   sky=['#101c4a', '#1a2a62', '#2a3a7a', '#44488e', '#6a549a', '#8e5a9c', '#b4609a', '#d46a90', '#ee7c82', '#f8966e', '#ffb472', '#ffd088', '#ffe6a8'],
   mont=['#8a5a8c', '#6e4a82', '#523c70', '#3a2e58', '#241c3c'], mist=['#f09a8a', '#d47a8c', '#a8628a', '#7a4e7e', '#4e3a66'],
   nieve=('#fff0e0', '#e8b8c8'), filo='#ffd8b0', pino1='#1c1230', pino2='#2a1c40', pinorim='#4a2c58',
   isla=('#1a1030', '#271a42', '#5a3a68'), ink=('#150c26', '#22143a', '#34204e'), techo_luz='#a86a90', bruma='#d89aa8', agua='#2c2050',
   ola=('#f0b8a0', '#9a6aa0', '#4a3a78'), cana=('#1a0e24', '#4a2a50', '#1e1228', '#5a3a60'), vig=0.80, boat='#1a0e24', tor_ref='#3a1a40',
   nube=['#c08aa8', '#e8a0a0', '#f0a890', '#ffc8a0', '#ffd0a0', '#9a78a8']),
 'dia': dict(
   sky=['#1e5aa8', '#2a68b8', '#3a78c6', '#4a88d2', '#5e98dc', '#74a8e4', '#8cb8ea', '#a4c8ee', '#bcd6f0', '#d0e2f0', '#e0ecee', '#eef2e8', '#f6f0dc'],
   mont=['#7a9cc0', '#5f88b0', '#4a7498', '#375e7c', '#244a58'], mist=['#d6e6f2', '#c4dcec', '#a8c8de', '#8ab4cc', '#6a9cb0'],
   nieve=('#ffffff', '#d8e8f4'), filo='#ffffff', pino1='#12342e', pino2='#1a4638', pinorim='#3a6a58',
   isla=('#173648', '#1f4a58', '#4a7a8a'), ink=('#142c40', '#1e3e52', '#2e566e'), techo_luz='#8ab8d0', bruma='#c8e0f0', agua='#1d5a8c',
   ola=('#cfe6f6', '#7ab4dc', '#3a78a8'), cana=('#0c2a22', '#2a5a44', '#0e2e24', '#3a6a50'), vig=0.92, boat='#122a38', tor_ref='#1c3a5a',
   nube=['#ffffff', '#f4f8ff', '#ffffff', '#fff6ee', '#ffffff', '#e8f0fa']),
}
PAL = PALETAS[FASE]
# ---------------------------------------------------------------- cielo
SKY = PAL['sky']
for y in range(HOR):
    t = (y / HOR) ** 1.45 * (len(SKY) - 1); i = int(t); f = t - i
    for x in range(W):
        put(x, y, (0, 0, 0) if SKYM == 'negro' else (255, 255, 255) if SKYM == 'blanco' else (SKY[min(i + 1, len(SKY) - 1)] if dith(x, y, f) else SKY[i]))

# via lactea: banda diagonal de polvo y estrellas finas
rl = Ruido(5)
for x in range(W):
    for y in range(0, 190):
        d = abs((y - (110 + (x - 60) * -0.42))) / 34.0
        if d < 1 and not en_zona(x, y, 20) and FASE == 'noche' and SKYM == 'normal':
            dens = (1 - d) ** 2 * (0.4 + 0.6 * rl(x * 0.06 + y * 0.05))
            if dith(x, y, dens * 0.34): over(x, y, '#b9a8e6', 0.45)
            if random.random() < dens * 0.018: put(x, y, '#e9e4ff')

if os.environ.get('PZ_SKYONLY'):
    import pickle; pickle.dump([r_[:] for r_ in px], open(os.environ['PZ_SKYONLY'], 'wb')); sys.exit(0)
# estrellas
for _ in range(430):
    x, y = random.randrange(W), random.randrange(int(HOR * 0.62))
    if en_zona(x, y) and random.random() < 0.85: continue
    b = random.random()
    col_e = '#f6efe0' if b > 0.7 else random.choice(['#cfd3ff', '#9aa0d8', '#7378b8'])
    if ANIM:
        ESTRELLAS.append([x, y, col_e, 1 if (b > 0.965 and not en_zona(x, y)) else 0]); continue
    put(x, y, col_e)
    if b > 0.965 and not en_zona(x, y):
        for k in (1, 2):
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): over(x + dx, y + dy, '#c7ccff', 0.8 / k)

# ---------------------------------------------------------------- luna detallada
MX, MY, MR = 352, 84, 46
def dibuja_luna(MX, MY, MR=46):
    for y in range(MY - 110, MY + 110):
        for x in range(MX - 110, MX + 110):
            d = math.hypot(x - MX, y - MY)
            if MR < d < 104 and 0 <= y < HOR and dith(x, y, ((104 - d) / (104 - MR)) ** 2.4 * 0.42): over(x, y, '#d6b0cc', 0.85)
    rm = Ruido(9)
    for y in range(MY - MR, MY + MR + 1):
        for x in range(MX - MR, MX + MR + 1):
            d = math.hypot(x - MX, y - MY)
            if d <= MR:
                c = mix('#f8efd8', '#e6d6b6', min(1, max(0, ((x - MX) * 0.55 + (y - MY) * 0.8) / MR * 0.5 + 0.2)))
                n = rm(x * 0.09) * 0.6 + rm(y * 0.11 + 40) * 0.4          # mares lunares
                if n > 0.56 and d < MR - 3: c = mix(c, '#cdbf9f', 0.55 if n > 0.62 else (0.3 if dith(x, y, 0.5) else 0.0))
                if d > MR - 3: c = mix(c, '#fff8e6', 0.5) if (x - MX) < 0 else mix(c, '#cbb994', 0.4)   # borde: luz / sombra
                put(x, y, c)
    for cx, cy, r in ((-17, -14, 7), (11, -22, 5), (18, 15, 9), (-21, 13, 5), (-3, 25, 4), (28, -6, 4), (-8, 2, 3), (4, 8, 2)):
        disc(MX + cx, MY + cy, r, '#d3c4a2'); disc(MX + cx - 1, MY + cy - 1, max(1, r - 2), '#e2d6b8')
        for k in range(-r, r): over(MX + cx + k, MY + cy + r, '#fff6dc', 0.5) if dith(k, r, 0.5) else None


def dibuja_sol(cx, cy, R=24):
    for y in range(cy - 104, cy + 104):
        for x in range(cx - 104, cx + 104):
            d = math.hypot(x - cx, y - cy)
            if R < d < 100 and dith(x, y, ((100 - d) / (100 - R)) ** 2.2 * 0.55): over(x, y, '#ffd890', 0.9)
    for y in range(cy - R, cy + R + 1):
        for x in range(cx - R, cx + R + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= R:
                c = mix('#fffbe0', '#ffcf60', (d / R) ** 1.4)
                if d > R - 2: c = '#ffb040' if dith(x, y, 0.6) else '#ffc860'
                put(x, y, c)
    for k in range(16):
        a = k / 16 * 2 * math.pi
        for t in range(R + 5, R + (16 if k % 2 == 0 else 11)):
            if t % 2 == 0: put(round(cx + math.cos(a) * t), round(cy + math.sin(a) * t), '#ffe08a')

if os.environ.get('PZ_SPRITES'):
    import pickle
    res = {}
    for nombre_, fn_ in (('luna', lambda: dibuja_luna(104, 104, 46)), ('sol', lambda: dibuja_sol(104, 104, 24))):
        bufs = []
        for fondo_ in ((0, 0, 0), (255, 255, 255)):
            for yy_ in range(208):
                for xx_ in range(208): px[yy_][xx_] = fondo_
            fn_(); bufs.append([row_[:208] for row_ in px[:208]])
        res[nombre_] = bufs
    pickle.dump(res, open(os.environ['PZ_SPRITES'], 'wb')); sys.exit(0)
if not ANIM: dibuja_luna(MX, MY, MR)

# ---------------------------------------------------------------- nubes finas (hebras con tramado)
def nube(cx, cy, w, col, grosor=3):
    if ANIM: NUBES.append([cx, cy, w, col, grosor]); return
    for k in range(grosor):
        ww = int(w * (1 - k * 0.16))
        for x in range(cx - ww // 2, cx + ww // 2):
            borde = 1 - abs(x - cx) / (ww / 2 + 1)
            if dith(x, cy + k * 2, 0.95 * borde ** 0.6 - k * 0.2): over(x, cy + k * 2, col, 0.85)
nube(160, 62, 190, PAL['nube'][0]); nube(380, 100, 150, PAL['nube'][1], 3); nube(90, 170, 210, PAL['nube'][2])
nube(270, 215, 170, PAL['nube'][3]); nube(560, 250, 120, PAL['nube'][4], 2); nube(430, 56, 90, PAL['nube'][5], 2)

# grullas lejanas
def grulla(x, y, e=1):
    for k in range(5 * e):
        put(x - k, y + k // 2 * (1 if e else 0) - (k // 3), '#120c26'); put(x + k, y + k // 2 - (k // 3), '#120c26')
    put(x, y + 1, '#120c26')
if not ANIM:
    for gx, gy in ((300, 128), (318, 118), (334, 134), (292, 150)): grulla(gx, gy, 1)

# ---------------------------------------------------------------- montanas
def rampa(x): return 1.0 if x < 420 else max(0.3, 1.0 - (x - 420) / 90 * 0.7)
CAPAS = [  # base, amp, semilla, frec, color, niebla, nieve
    (236, 112, 1, 0.011, PAL['mont'][0], PAL['mist'][0], True),
    (249, 96, 2, 0.015, PAL['mont'][1], PAL['mist'][1], False),
    (260, 80, 3, 0.020, PAL['mont'][2], PAL['mist'][2], False),
    (270, 60, 4, 0.027, PAL['mont'][3], PAL['mist'][3], False),
    (279, 38, 5, 0.036, PAL['mont'][4], PAL['mist'][4], False)]
crestas = []
for base, amp, seed, fr, col, mist, nieve in CAPAS:
    r = Ruido(seed * 17); ra = Ruido(seed * 53 + 1); c = []
    for x in range(W):
        n = fbm(r, x * fr * 1.5 + seed)
        agudo = 1 - abs(2 * n - 1); suave = n
        am = 0.30 + 0.95 * ra(x * 0.011 + seed) ** 1.3                 # picos grandes y valles
        c.append(base - amp * rampa(x) * am * (0.62 * agudo + 0.38 * suave))
    crestas.append(c)
    rt = Ruido(seed * 31)
    for x in range(W):
        top = int(c[x]); pend = c[min(W - 1, x + 2)] - c[max(0, x - 2)]
        for y in range(top, HOR + 1):
            d = y - top; cc = col
            prof = d / max(1, (HOR - top))
            cc = mix(cc, mist, 0.26 * prof ** 2.2)                          # bruma al pie
            if nieve and top < base - amp * 0.50 * rampa(x) and d < (base - amp * 0.50 * rampa(x) - top) * 0.62 + (3 if dith(x, y, 0.5) else 0) - 2 * abs(rt(x * 0.2) - 0.5) * 6:
                cc = mix(PAL['nieve'][0], PAL['nieve'][1], min(1, d / 14.0))               # nieve
            elif d > 5 and (x + 2 * y) % 11 == 0 and dith(x, y, 0.8): cc = mix(cc, '#000010', 0.18)   # estratos
            elif d > 8 and (y // 9 + (x // 23)) % 5 == 0 and dith(x, y, 0.35): cc = mix(cc, mist, 0.13)
            if d < 2: cc = mix(cc, PAL['filo'], 0.30 if pend < 0 else 0.07)       # filo con luz de luna
            put(x, y, cc)
        for k in range(1, 26):                                              # niebla sobre la cresta
            if dith(x, top + k, (1 - k / 26) * 0.5): over(x, top + k, mist, 0.65)
    # banda de niebla horizontal entre capas
    by = int(base + 2)
    for x in range(W):
        for k in range(-5, 6):
            if dith(x, by + k, (1 - abs(k) / 6) * 0.30): over(x, by + k, mist, 0.5)

def pino(x, by, h, col, rim=PAL['pinorim']):
    for i in range(h):
        y = by - h + i; hw = max(0, int(i * 0.33) - (2 if i % 5 == 4 else 0));
        for dx in range(-hw, hw + 1): put(x + dx, y, col)
        if hw > 1 and i % 5 != 4: over(x - hw, y, rim, 0.55)
    for i in range(4): put(x, by + i, col)
r5 = random.Random(77)
for x in range(0, W, 4):
    if r5.random() < 0.8:
        pino(x + r5.randint(-1, 1), int(crestas[4][x]) + 6, r5.randint(9, 20), PAL['pino1'])
for x in range(0, W, 7):
    if r5.random() < 0.6: pino(x, int(crestas[3][x]) + 5, r5.randint(7, 13), PAL['pino2'])

# ---------------------------------------------------------------- isla, templo y pagoda
INK, INK2, INK3 = PAL['ink']; WARM = '#f2b866'
def mancha_isla(cx, w, h):
    for y in range(HOR - h, HOR + 1):
        t = (HOR - y) / h
        ww = int(w * (1 - t ** 1.8) / 2)
        for x in range(cx - ww, cx + ww):
            c = PAL['isla'][0] if (x + y) % 5 else PAL['isla'][1]
            if (HOR - y) > h - 3: c = PAL['isla'][2]
            put(x, y, c)
mancha_isla(213, 190, 34)

def techo(cx, y, w, h, c=INK):
    for i in range(h):
        ww = w - int(i * (w * 0.5 / h) * 1.2)
        for x in range(cx - ww // 2, cx + ww // 2 + 1): put(x, y + i, c)
    for k in range(6):                               # aleros curvados hacia arriba
        yy = y - (k + 1) // 2 + 1
        put(cx - w // 2 - k, yy, c); put(cx + w // 2 + k, yy, c)
        if k < 3: put(cx - w // 2 - k, yy + 1, c); put(cx + w // 2 + k, yy + 1, c)
    for x in range(cx - w // 2 + 2, cx + w // 2 - 1, 2): over(x, y + h - 1, PAL['techo_luz'], 0.8)   # borde iluminado
def cuerpo(cx, y, w, h):
    for yy in range(y, y + h):
        for x in range(cx - w // 2, cx + w // 2 + 1): put(x, yy, INK2)
    for x in range(cx - w // 2, cx + w // 2 + 1, 6):                                      # pilares
        for yy in range(y, y + h): put(x, yy, INK)
    for x in range(cx - w // 2 + 3, cx + w // 2 - 2, 6):                                  # ventanas con luz
        if ANIM: VENTANAS.append([x, y + 3]); continue
        for yy in (y + 3, y + 4, y + 5, y + 6): put(x, yy, WARM); put(x + 1, yy, WARM)
        glow(x, y + 5, 4, WARM, 0.35)
    for x in range(cx - w // 2 - 2, cx + w // 2 + 3): put(x, y + h, INK3) if x % 2 == 0 else put(x, y + h, INK)  # barandilla
def farol(x, y):
    if ANIM: FAROLES.append([x, y, 6]); return
    put(x, y, WARM); put(x, y + 1, WARM); put(x, y - 1, '#7a4a3a'); glow(x, y, 6, WARM, 0.55)

PX, PB = 213, HOR - 30
tiers = [(46, 13), (40, 12), (34, 11), (28, 10), (22, 9)]
y = PB
for i, (bw, bh) in enumerate(tiers):
    cuerpo(PX, y - bh, bw - 8, bh); techo(PX, y - bh - 7, bw + 14, 7); farol(PX - bw // 2 - 8, y - bh - 2); farol(PX + bw // 2 + 8, y - bh - 2)
    y -= bh + 8
for k in range(18): put(PX, y - k, INK)
for k, yy in enumerate((y - 4, y - 8, y - 12, y - 15)):
    for dx in range(-3 + k // 2, 4 - k // 2): put(PX + dx, yy, INK)
if ANIM: FAROLES.append([PX, y - 19, 5])
else: put(PX, y - 19, WARM); glow(PX, y - 19, 5, WARM, 0.5)
# salon a la izquierda
cuerpo(140, HOR - 28, 40, 14); techo(140, HOR - 36, 64, 9); farol(106, HOR - 36); farol(174, HOR - 36)
# salon a la derecha mas pequeño
cuerpo(290, HOR - 20, 26, 10); techo(290, HOR - 26, 44, 7)
# escalinata y faroles de piedra
for yy in range(HOR - 14, HOR):
    for x in range(PX - 8 - (HOR - yy) // 2, PX + 9 + (HOR - yy) // 2): over(x, yy, PAL['isla'][2], 0.7) if (x + yy) % 4 == 0 else None
def toro(x, y):
    for yy in range(6): put(x, y - yy, '#16143a'); put(x + 1, y - yy, '#16143a')
    for xx in range(-3, 5): put(x + xx, y - 8, '#1e1a42'); put(x + xx, y - 7, '#16143a')
    if ANIM: FAROLES.append([x, y - 7, 5])
    else: put(x, y - 7, WARM); put(x + 1, y - 7, WARM); glow(x, y - 6, 5, WARM, 0.45)
    for xx in range(-1, 3): put(x + xx, y - 9, '#16143a')
toro(160, HOR - 6); toro(262, HOR - 6); toro(78, HOR - 4)
for x0, ww in ((60, 20), (330, 30)):
    for _ in range(ww * 3): put(x0 + random.randint(-ww, ww), HOR - random.randint(0, 5), PAL['isla'][0])

# bruma baja sobre el agua (une montañas y lago)
for y in range(HOR - 22, HOR + 1):
    for x in range(W):
        if dith(x, y, ((y - (HOR - 22)) / 22.0) ** 1.6 * 0.34): over(x, y, PAL['bruma'], 0.55)

# ---------------------------------------------------------------- lago
copia = [list(r) for r in px[:HOR + 1]]
for y in range(HOR + 1, H):
    d = y - HOR; src = HOR - 1 - int(d * 1.12)
    for x in range(W):
        ond = int(2.2 * math.sin(d * 0.55 + x * 0.025)) + (2 if (d // 3) % 2 else -2)
        sx = (x + ond) % W
        k = max(0.12, 0.62 - d * 0.0045)
        c = mix(PAL['agua'], copia[max(src, 0)][sx], k)
        put(x, y, c)
rr = random.Random(21)
for y in range(HOR + 2, H, 3):                             # brillos de olas
    for _ in range(40):
        x = rr.randrange(W); l = rr.randint(4, 24)
        c = PAL['ola'][0] if y < HOR + 40 else (PAL['ola'][1] if y < HOR + 80 else PAL['ola'][2])
        for k in range(l): over(x + k, y, c, 0.7 - (y - HOR) * 0.002)
for d in (range(8, 120, 3) if not ANIM else ()):           # camino de la luna en el agua
    ww = int(46 - d * 0.30)
    if ww < 3: break
    for x in range(MX - ww // 2, MX + ww // 2):
        if rr.random() < 0.55 - d * 0.003: put(x, HOR + d, '#f4e2c4' if d < 50 else '#cdaacc')
for _ in range(220):                                       # destellos
    x, y = rr.randrange(300, 410), HOR + rr.randrange(6, 100)
    if ANIM: DESTELLOS.append([x, y]); continue
    put(x, y, '#fff4dc'); over(x + 1, y, '#fff4dc', 0.6)

# ---------------------------------------------------------------- torii grande con reflejo
TX, TBY = 437, 340
def torii(cx, by, plot):
    R, R2, R3 = '#c8382e', '#8a2420', '#e0584a'; h, sep = 56, 46
    for dx in (-sep // 2, sep // 2):
        for yy in range(by - h, by):
            for t in range(-3, 4): plot(cx + dx + t, yy, R3 if t == -3 else (R2 if t >= 2 else R))
    for yy in range(by - h - 4, by - h + 3):
        for x in range(cx - sep // 2 - 20, cx + sep // 2 + 21): plot(x, yy, R if yy < by - h + 1 else R2)
    for k in range(8):
        plot(cx - sep // 2 - 20 - k, by - h - 4 - (k + 1) // 2, R); plot(cx + sep // 2 + 20 + k, by - h - 4 - (k + 1) // 2, R)
        if k < 3: plot(cx - sep // 2 - 20 - k, by - h - 3 - (k + 1) // 2, R); plot(cx + sep // 2 + 20 + k, by - h - 3 - (k + 1) // 2, R)
    for yy in range(by - h + 3, by - h + 7):
        for x in range(cx - sep // 2 - 16, cx + sep // 2 + 17): plot(x, yy, '#1c0e18' if yy == by - h + 6 else R2)
    for yy in range(by - h + 16, by - h + 22):
        for x in range(cx - sep // 2 - 5, cx + sep // 2 + 6): plot(x, yy, R)
    for yy in range(by - h + 7, by - h + 16):                    # placa central
        for x in range(cx - 4, cx + 5): plot(x, yy, '#16101e')
    for yy in range(by - h - 4, by - h + 3): plot(cx, yy, R2)
mask = {}
torii(TX, TBY, lambda x, y, c: mask.__setitem__((x, y), hx(c)))
for dy in range(0, 76):
    if dy % 4 == 3: continue
    sh = 1 if (dy // 2) % 2 else -1; a = max(0.1, 0.62 - dy * 0.006)
    for (x, y), c in mask.items():
        if y == TBY - 1 - dy and 0 <= x + sh < W and TBY + dy < H:
            over(x + sh, TBY + dy, mix(c, PAL['tor_ref'], 0.4), a)
for dx in (-23, 23):
    for yy in range(TBY - 5, TBY + 1):
        for x in range(TX + dx - 8, TX + dx + 9): put(x, yy, '#52468a' if yy == TBY - 5 else ('#3a3170' if yy == TBY - 4 else '#252048'))
    for x in range(TX + dx - 15, TX + dx + 16):
        if abs(x - (TX + dx)) > 8 and dith(x, TBY + 1, 0.6): over(x, TBY + 1, '#c3a4c8', 0.8)
torii(TX, TBY - 5, put)

# ---------------------------------------------------------------- barca con farol
BX, BY = 300, 318
for i in range(40):                                        # casco
    t = i / 39.0; yy = BY + int(4 * (1 - (2 * t - 1) ** 2) + 0.5)
    for k in range(0, 4): put(BX - 20 + i, BY + k + int((2 * t - 1) ** 2 * -3) + 3 - 3, PAL['boat'])
for i in range(-20, 21): put(BX + i, BY + 4 - int((i / 20.0) ** 2 * 3), PAL['boat'])
for x in range(BX - 8, BX + 6): put(x, BY - 1, PAL['boat'])
for yy in range(BY - 14, BY - 1): put(BX + 12, yy, PAL['boat'])                              # mastil / farol
if ANIM: FAROLES.append([BX + 12, BY - 15, 11])
else:
    put(BX + 12, BY - 15, WARM); put(BX + 12, BY - 16, WARM); put(BX + 11, BY - 15, WARM); put(BX + 13, BY - 15, WARM)
    glow(BX + 12, BY - 15, 11, WARM, 0.75)
for yy in range(BY - 9, BY - 1):                                                          # remero con sombrero
    put(BX - 3, yy, PAL['boat']); put(BX - 2, yy, PAL['boat'])
for x in range(BX - 6, BX + 2): put(x, BY - 10, PAL['boat'])
for d in range(5, 60, 2):                                                                  # reflejo del farol
    for x in range(BX + 12 - (3 if d < 30 else 5), BX + 12 + (3 if d < 30 else 5)):
        if dith(x, BY + 6 + d, 0.8 - d * 0.012): over(x + (1 if (d // 2) % 2 else -1), BY + 6 + d, WARM, 0.8 - d * 0.01)
for x in range(BX - 24, BX + 26):
    if x % 3: over(x, BY + 8, '#2a2450', 0.7)

# ---------------------------------------------------------------- cañas y rocas en primer plano
rcn = random.Random(5)
def cana(x, h, curva, col, borde):
    for i in range(h):
        xx = x + int(curva * (i / h) ** 2 * 10); put(xx, H - 1 - i, col)
        if i % 2 == 0: put(xx + 1, H - 1 - i, col)
        if i > 4: over(xx - 1, H - 1 - i, borde, 0.5)
    if h > 40:                                                                              # espiga
        for k in range(8): put(x + int(curva * 10) + (0 if k < 6 else 0), H - h - k, '#2b1a2e'); put(x + int(curva * 10) + 1, H - h - k, '#2b1a2e')
for x in list(range(0, 150, 3)) + list(range(520, 640, 4)):
    if rcn.random() < 0.8: cana(x + rcn.randint(-2, 2), rcn.randint(20, 90) - (30 if x > 440 else 0), rcn.uniform(-1, 1), PAL['cana'][0], PAL['cana'][1])
for cx0, ww in ((40, 60), (610, 40)):
    for x in range(cx0 - ww, cx0 + ww):
        t = (x - cx0) / ww; hh = int(18 * (1 - t * t) ** 0.8)
        for k in range(hh): put(x, H - 1 - k, PAL['cana'][2] if k < hh - 2 else PAL['cana'][3])
# luciernagas
for fx, fy in ((70, 300), (95, 330), (130, 290), (565, 310), (590, 340), (20, 345), (470, 296), (160, 355)):
    if ANIM: continue
    put(fx, fy, '#eaf5a0'); glow(fx, fy, 6, '#c9e86a', 0.7)

# ---------------------------------------------------------------- rama de cerezo (esquina sup. izq.)
RAMA, RAMA2 = '#130a1b', '#2c1a30'
def rama(pts, r0, r1):
    n = sum(max(abs(b[0] - a[0]), abs(b[1] - a[1])) for a, b in zip(pts, pts[1:])) or 1; i = 0
    for a, b in zip(pts, pts[1:]):
        m = max(abs(b[0] - a[0]), abs(b[1] - a[1])) or 1
        for k in range(m + 1):
            r = r0 + (r1 - r0) * (i / n); i += 1
            cx = a[0] + (b[0] - a[0]) * k // m; cy = a[1] + (b[1] - a[1]) * k // m
            disc(cx, cy, max(1, round(r)), RAMA)
            if r > 2: put(cx - round(r) + 1, cy - round(r) + 1, RAMA2)                       # veta clara
        i -= 1
rama([(-10, 26), (24, 38), (64, 50), (104, 56), (146, 56), (186, 70), (236, 70)], 7, 1.5)
rama([(64, 50), (78, 86), (92, 112), (78, 150)], 5, 1.2)
rama([(146, 56), (168, 26), (204, 12)], 3.5, 1)
rama([(186, 70), (200, 104), (214, 128)], 3.5, 1)
rama([(24, 38), (38, 12), (44, -2)], 3.5, 1)
rama([(104, 56), (122, 88), (138, 110)], 2.5, 1)
rama([(236, 70), (262, 66), (282, 74)], 1.5, 1)
ROSA = {'l': '#fdeff3', 'c': '#f7cfdb', 'm': '#eda0b8', 'd': '#cf6f90', 'x': '#9a456c'}
def flor(cx, cy, v, grande):
    tono = 'l' if v < -0.35 else ('c' if v < 0.05 else ('m' if v < 0.45 else 'd'))
    if random.random() < 0.18: tono = {'l': 'c', 'c': 'l', 'm': 'c', 'd': 'm'}[tono]
    r = 2 if grande else 1
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if (abs(dx) == r and abs(dy) == r) and random.random() < 0.6: continue
            put(cx + dx, cy + dy, ROSA[tono])
    put(cx, cy, '#f0b84a' if random.random() < 0.55 else ROSA['x'])
    if grande: put(cx - 1, cy - 1, ROSA['l'])
def racimo(cx, cy, R):
    cells = {}
    for _ in range(int(R * 0.9) + 4):
        ox, oy = random.randint(-R // 2, R // 2), random.randint(-R // 2, R // 2)
        disc(cx + ox, cy + oy, random.randint(max(3, R // 3), max(4, R // 2)), 1, lambda x, y, c: cells.__setitem__((x, y), 1))
    for _ in range(len(cells) // 7):
        x, y = random.choice(list(cells)); v = ((x - cx) + (y - cy)) / (2.0 * R)
        flor(x, y, v + random.uniform(-0.25, 0.25), random.random() < 0.55)
    for _ in range(max(3, R // 3)):
        a = random.random() * 6.28; rr_ = R * 0.55 + random.random() * 8
        put(int(cx + math.cos(a) * rr_), int(cy + math.sin(a) * rr_), random.choice((ROSA['c'], ROSA['m'], ROSA['d'])))
for cx, cy, R in ((14, 30, 26), (56, 46, 24), (100, 54, 28), (146, 54, 28), (180, 38, 20), (210, 14, 20), (186, 72, 24), (236, 70, 18),
                  (74, 98, 22), (82, 136, 20), (210, 112, 20), (136, 100, 18), (44, 8, 20), (270, 70, 14), (110, 80, 14), (20, 70, 12),
                  (120, 52, 16), (162, 64, 14), (90, 58, 14), (36, 40, 14)):
    racimo(cx, cy, R)
for _ in range(110):                                       # petalos al viento
    x, y = random.randrange(W), random.randrange(0, 360)
    if en_zona(x, y, 10) or ANIM: continue
    c = random.choice((ROSA['c'], ROSA['m'], ROSA['l']))
    put(x, y, c); put(x + 1, y + 1, ROSA['m'])
    if random.random() < 0.4: put(x + 1, y, ROSA['l'])

# ---------------------------------------------------------------- vineta
for y in range(H):
    for x in range(W):
        d = math.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2))
        if d > 0.82 and dith(x, y, (d - 0.82) * 0.95):
            r, g, b = px[y][x]; px[y][x] = (int(r * PAL['vig']), int(g * PAL['vig']), int(b * (PAL['vig'] + 0.06)))

# ---------------------------------------------------------------- PNG
def png(ruta, buf):
    raw = bytearray()
    for y in range(H):
        fila = b''.join(bytes(buf[y][x]) * S for x in range(W)); raw += (b'\x00' + fila) * S
    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(ruta, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W * S, H * S, 8, 2, 0, 0, 0))
                + ch(b'IDAT', zlib.compress(bytes(raw), 9)) + ch(b'IEND', b''))

out = ARGS[0] if ARGS else '.'
os.makedirs(out, exist_ok=True)
if ANIM:
    # nubes: hoja de sprites RGBA (cada nube en su fila), con el mismo tramado
    filas_n, sprites, y0 = [], [], 0
    for cx, cy, w, col, gr in NUBES:
        h = gr * 2; buf = [[(0, 0, 0, 0)] * w for _ in range(h)]
        for k in range(gr):
            ww = int(w * (1 - k * 0.16))
            for xx in range(cx - ww // 2, cx + ww // 2):
                borde = 1 - abs(xx - cx) / (ww / 2 + 1)
                if dith(xx, cy + k * 2, 0.95 * borde ** 0.6 - k * 0.2):
                    r_, g_, b_ = hx(col); buf[k * 2][xx - (cx - w // 2)] = (r_, g_, b_, 217)
        sprites.append([cx - w // 2, cy, w, h, y0]); filas_n += buf; y0 += h
    SW = max(n[2] for n in NUBES)
    raw = bytearray()
    for fila in filas_n:
        fila = list(fila) + [(0, 0, 0, 0)] * (SW - len(fila))
        raw += b'\x00' + b''.join(bytes(p) for p in fila)
    def chk(t, d):
        c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(os.path.join(out, f'nubes-{FASE}.png'), 'wb').write(b'\x89PNG\r\n\x1a\n' + chk(b'IHDR', struct.pack('>IIBBBBB', SW, len(filas_n), 8, 6, 0, 0, 0))
                                                    + chk(b'IDAT', zlib.compress(bytes(raw), 9)) + chk(b'IEND', b''))
    datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, destellos=DESTELLOS, nubes=sprites, nubes_w=SW, barca=[BX, BY], luna=[MX, MY, MR])
    open(os.path.join(out, 'datos.js'), 'w').write('.pragma library\nvar D = ' + json.dumps(datos) + ';\n')
    if os.environ.get('PZ_DUMP'):
        import pickle; pickle.dump([r_[:] for r_ in px], open(os.environ['PZ_DUMP'], 'wb'))
    print('anim ok', len(ESTRELLAS), 'estrellas', len(VENTANAS), 'ventanas', len(FAROLES), 'luces', len(DESTELLOS), 'destellos', len(NUBES), 'nubes')
    sys.exit(0)
png(os.path.join(out, 'v3.png'), px)

# ========== vista previa con maqueta de widgets ==========
F = {'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
     'E': '111100110100111', 'F': '111100110100100', 'G': '011100101101011', 'H': '101101111101101',
     'I': '111010010010111', 'K': '101101110101101', 'L': '100100100100111', 'M': '101111111101101',
     'N': '110101101101101', 'O': '010101101101010', 'P': '110101110100100', 'R': '110101110101101',
     'S': '011100010001110', 'T': '111010010010010', 'U': '101101101101111', 'V': '101101101101010',
     'W': '101101111111101', 'X': '101101010101101', 'Y': '101101010010010',
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
    for a, b, c, d in ((x0, y0, x1, y0 + 1), (x0, y1 - 1, x1, y1), (x0, y0, x0 + 1, y1), (x1 - 1, y0, x1, y1)): rect(buf, a, b, c, d, '#6a4a8a')
    rect(buf, x0, y0, x0 + 6, y0 + 1, '#c8382e'); rect(buf, x0, y0, x0 + 1, y0 + 6, '#c8382e')
WASHI, LAB = '#f3e9d2', '#b8708a'
pv = [list(r) for r in px]
X0, X1 = 488, 628
panel(pv, X0, 14, X1, 74)
texto(pv, X0 + 12, 22, '14:32', WASHI, 4); texto(pv, X0 + 12, 54, 'DOM 01 NOV', LAB, 2)
rect(pv, X1 - 22, 22, X1 - 12, 32, '#c8382e')
panel(pv, X0, 82, X1, 150)
for i, (n, v, c) in enumerate((('CPU', 23, '#c8382e'), ('RAM', 41, '#e0b36a'), ('TMP', 52, '#7fb88a'))):
    yy = 92 + i * 18; texto(pv, X0 + 10, yy, n, LAB, 2)
    rect(pv, X0 + 44, yy + 2, X0 + 104, yy + 8, '#2b2850'); rect(pv, X0 + 44, yy + 2, X0 + 44 + 60 * v // 100, yy + 8, c)
    texto(pv, X0 + 110, yy, f'{v}%', WASHI, 2)
panel(pv, X0, 158, X1, 226)
for i, (a, b) in enumerate((('NET', 'WLAN0 UP'), ('VPN', 'OFF'), ('GIT', 'MAIN +3'), ('DKR', '2 UP'))):
    yy = 166 + i * 14; texto(pv, X0 + 10, yy, a, LAB, 2); texto(pv, X0 + 50, yy, b, WASHI, 2)
png(os.path.join(out, 'v3-preview.png'), pv)

K = 2.4   # fisico (x3) -> logico (x2.4)
caja = {'reloj': [X0, 14, X1, 74], 'sistema': [X0, 82, X1, 150], 'red_dev': [X0, 158, X1, 226]}
json.dump({'cuadricula': [W, H], 'escala_fisica': S, 'zona_widgets': {'x': [ZX0, ZX1], 'y': [ZY0, ZY1]},
           'paneles_fisicos': {k: [v[0] * S, v[1] * S, v[2] * S, v[3] * S] for k, v in caja.items()},
           'paneles_logicos': {k: [round(v[0] * K), round(v[1] * K), round(v[2] * K), round(v[3] * K)] for k, v in caja.items()}},
          open(os.path.join(out, 'zonas.json'), 'w'), indent=2)
print('ok', W * S, H * S)
