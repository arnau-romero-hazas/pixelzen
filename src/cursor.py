#!/usr/bin/env python3
"""PixelZen - cursor pixel art (formato Xcursor, sin dependencias).
Arte en rejilla 16x16; se escala x1,x2,x3,x4 (16,32,48,64 px). Salida: tema/cursor/PixelZenCursor."""
import os, shutil, struct

OUT = os.path.expanduser('~/.local/share/pixelzen/tema/cursor/PixelZenCursor')
COL = {'X': (10, 12, 36), 'o': (243, 233, 210), 'r': (224, 82, 74), 'v': (138, 74, 121), 'g': (127, 184, 138), 'a': (224, 179, 106), 'c': (127, 196, 196), 'p': (242, 184, 198)}

def vacio(): return [['.'] * 16 for _ in range(16)]
def linea(g, x0, y0, x1, y1, c='o'):
    n = max(abs(x1 - x0), abs(y1 - y0)) or 1
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        if 0 <= x < 16 and 0 <= y < 16: g[y][x] = c
def contorno(g):
    """rodea de 'X' los pixeles de color (como borde oscuro)."""
    r = [fila[:] for fila in g]
    for y in range(16):
        for x in range(16):
            if g[y][x] != '.' and g[y][x] != 'X':
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < 16 and 0 <= yy < 16 and r[yy][xx] == '.': r[yy][xx] = 'X'
    return r
def desde(filas, ox=0, oy=0, g=None):
    g = g or vacio()
    for y, f in enumerate(filas):
        for x, ch in enumerate(f):
            if ch != '.' and 0 <= x + ox < 16 and 0 <= y + oy < 16: g[y + oy][x + ox] = ch
    return g

FLECHA = ['X', 'XX', 'XoX', 'XooX', 'XoooX', 'XooooX', 'XoooooX', 'XooooooX', 'XoooooooX', 'XooooooXXX', 'XooXooX', 'XoXXooX', 'XX..XooX', 'X...XooX', '.....XooX', '.....XXX']
def flecha(extra=None):
    g = desde(FLECHA)
    for x, y in ((0, 0), (0, 1), (1, 1), (0, 2)): g[y][x] = 'r'      # punta roja (torii)
    if extra: extra(g)
    return g, (0, 0)

def manita():
    f = ['....XX..........', '...XooX.........', '...XooX.........', '...XooX.........', '...XooXXX.......', '...XooXooXXX....', '.XXXooXooXooXX..',
         'XooXooooooooooX.', 'XoooooooooooooX.', '.XooooooooooooX.', '..XoooooooooooX.', '..XoooooooooooX.', '...XooooooooooX.', '...XooooooooooX.',
         '....XoooooooooX.', '....XXXXXXXXXXX.']
    g = desde(f)
    for x, y in ((4, 0), (5, 0), (4, 1)): g[y][x] = 'r'
    return g, (4, 0)

def ibeam(rot=False):
    g = vacio()
    for x in range(5, 10): g[0][x] = 'X'; g[15][x] = 'X'
    for x in (6, 7, 8): g[1][x] = 'o'; g[14][x] = 'o'
    for x in (5, 9): g[1][x] = 'X'; g[14][x] = 'X'
    for y in range(2, 14):
        g[y][6] = 'X'; g[y][7] = 'o'; g[y][8] = 'X'
    g[2][5] = 'X'; g[2][9] = 'X'; g[13][5] = 'X'; g[13][9] = 'X'
    if rot: g = [[g[x][y] for x in range(16)] for y in range(16)]
    return g, (7, 8)

def cruz():
    g = vacio()
    for a, b in (((7, 1), (7, 5)), ((7, 9), (7, 13)), ((1, 7), (5, 7)), ((9, 7), (13, 7))): linea(g, *a, *b)
    g[7][7] = 'r'; return contorno(g), (7, 7)

def flechas(dirs, diag=None):
    g = vacio()
    if diag == 'nwse':
        linea(g, 3, 3, 12, 12)
        for a, b in (((3, 3), (7, 3)), ((3, 3), (3, 7)), ((12, 12), (8, 12)), ((12, 12), (12, 8))): linea(g, *a, *b)
    elif diag == 'nesw':
        linea(g, 12, 3, 3, 12)
        for a, b in (((12, 3), (8, 3)), ((12, 3), (12, 7)), ((3, 12), (7, 12)), ((3, 12), (3, 8))): linea(g, *a, *b)
    else:
        h = 2 if len(dirs) > 1 else 3          # puntas mas cortas cuando hay cuatro flechas
        if 'h' in dirs:
            linea(g, 2, 7, 13, 7)
            for a, b in (((2, 7), (2 + h, 7 - h)), ((2, 7), (2 + h, 7 + h)), ((13, 7), (13 - h, 7 - h)), ((13, 7), (13 - h, 7 + h))): linea(g, *a, *b)
        if 'v' in dirs:
            linea(g, 7, 2, 7, 13)
            for a, b in (((7, 2), (7 - h, 2 + h)), ((7, 2), (7 + h, 2 + h)), ((7, 13), (7 - h, 13 - h)), ((7, 13), (7 + h, 13 - h))): linea(g, *a, *b)
    return contorno(g), (7, 7)

def prohibido():
    g = vacio()
    import math
    for i in range(64):
        a = i / 64 * 2 * math.pi
        x, y = round(7.5 + 6 * math.cos(a)), round(7.5 + 6 * math.sin(a))
        if 0 <= x < 16 and 0 <= y < 16: g[y][x] = 'r'
    linea(g, 3, 12, 12, 3, 'r')
    return contorno(g), (7, 7)

def girando(frame, con_flecha=False):
    g = vacio()
    import math
    for i in range(8):
        a = i / 8 * 2 * math.pi - math.pi / 2
        x, y = round(7.5 + 5.2 * math.cos(a)), round(7.5 + 5.2 * math.sin(a))
        d = (i - frame) % 8
        c = 'o' if d == 0 else 'p' if d == 1 else 'v' if d in (2, 3) else 'X'
        for dy in (0, 1):
            for dx in (0, 1): g[y + dy - 0][x + dx - 0] = c if 0 <= x + dx < 16 and 0 <= y + dy < 16 else g[y][x]
    return contorno(g), (7, 7)

def ayuda():
    def extra(g):
        for x, y in ((9, 8), (10, 8), (11, 9), (11, 10), (10, 11), (10, 12), (10, 14)): g[y][x] = 'o'
        for d in [(8, 9)]: pass
    g, h = flecha(extra)
    for x, y in ((9, 8), (10, 8), (11, 9), (11, 10), (10, 11), (10, 12), (10, 14)):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if g[y + dy][x + dx] == '.': g[y + dy][x + dx] = 'X'
    for x, y in ((9, 8), (10, 8), (11, 9), (11, 10), (10, 11), (10, 12), (10, 14)): g[y][x] = 'a'
    return g, h

def con_signo(simbolo):
    g, h = flecha()
    pts = {'+': [(11, 9), (11, 10), (11, 11), (11, 12), (11, 13), (9, 11), (10, 11), (12, 11), (13, 11)],
           'l': [(9, 10), (10, 10), (11, 10), (12, 10), (12, 11), (12, 12), (12, 13), (11, 12), (10, 13)],
           'm': [(9, 10), (10, 10), (11, 10), (12, 10), (9, 12), (10, 12), (11, 12), (12, 12), (9, 14), (10, 14), (11, 14), (12, 14)]}[simbolo]
    for x, y in pts:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < 16 and 0 <= y + dy < 16 and g[y + dy][x + dx] == '.': g[y + dy][x + dx] = 'X'
    for x, y in pts: g[y][x] = 'g' if simbolo == '+' else 'o'
    return g, h

def mano_abierta():
    f = ['....X.X.X.......', '...XoXoXoX......', '...XoXoXoXX.....', '..XXoooooooX....', '.XooXooooooX....', '.XoooooooooX....', '..XooooooooX....',
         '..XooooooooX....', '...XoooooooX....', '...XoooooooX....', '....XXXXXXXX....']
    return desde(f, 1, 2), (7, 7)
def puno():
    f = ['...XXXXXXXX.....', '..XoXoXoXoXX....', '..XooooooooX....', '..XooooooooX....', '..XoooooooooX...', '...XooooooooX...', '...XoooooooX....', '....XXXXXXXX....']
    return desde(f, 1, 4), (7, 8)
def lupa(mas):
    g = vacio()
    import math
    for i in range(48):
        a = i / 48 * 2 * math.pi
        x, y = round(6.5 + 4.5 * math.cos(a)), round(6.5 + 4.5 * math.sin(a)); g[y][x] = 'o'
    linea(g, 10, 10, 14, 14, 'o'); linea(g, 11, 10, 14, 13, 'o')
    linea(g, 4, 6, 8, 6, 'c')
    if mas: linea(g, 6, 4, 6, 8, 'c')
    return contorno(g), (6, 6)

BASE = {'default': lambda: flecha(), 'pointer': manita, 'text': lambda: ibeam(), 'vertical-text': lambda: ibeam(True), 'crosshair': cruz,
        'move': lambda: flechas('hv'), 'ew-resize': lambda: flechas('h'), 'ns-resize': lambda: flechas('v'),
        'nwse-resize': lambda: flechas('', 'nwse'), 'nesw-resize': lambda: flechas('', 'nesw'), 'not-allowed': prohibido,
        'help': ayuda, 'copy': lambda: con_signo('+'), 'alias': lambda: con_signo('l'), 'context-menu': lambda: con_signo('m'),
        'grab': mano_abierta, 'grabbing': puno, 'zoom-in': lambda: lupa(True), 'zoom-out': lambda: lupa(False)}
ANIM = {'wait': lambda f: girando(f), 'progress': lambda f: girando(f)}
ALIAS = {
 'default': 'left_ptr arrow top_left_arrow left_ptr_help X_cursor right_ptr draft_large draft_small dnd-ask dnd-move dnd-link',
 'pointer': 'hand hand1 hand2 pointing_hand openhand e29285e634086352946a0e7090d73106 9d800788f1b08800ae810202380a0822 08e8e1c95fe2fc01f976f1e063a24ccd',
 'text': 'xterm ibeam', 'crosshair': 'cross tcross cross_reverse diamond_cross plus cell', 'move': 'fleur all-scroll size_all grab-all dnd-none',
 'ew-resize': 'col-resize sb_h_double_arrow size_hor h_double_arrow e-resize w-resize split_h left_side right_side 14fef782d02440884392942c11205230',
 'ns-resize': 'row-resize sb_v_double_arrow size_ver v_double_arrow n-resize s-resize split_v top_side bottom_side 2870a09082c103050810ffdffffe0204',
 'nwse-resize': 'size_fdiag nw-resize se-resize top_left_corner bottom_right_corner c7088f0f3e6c8088236ef8e1e3e70000 bd_double_arrow',
 'nesw-resize': 'size_bdiag ne-resize sw-resize top_right_corner bottom_left_corner fcf1c3c7cd4491d801f1e1c78f100000 fd_double_arrow',
 'not-allowed': 'crossed_circle no-drop forbidden circle dnd-no-drop 03b6e0fcb3499374a867c041f52298f0', 'help': 'question_arrow whats_this left_ptr_help d9ce0ab605698f320427677b458ad60b',
 'grabbing': 'closedhand dnd-grabbing fcf21c00b30f7e3f83fe0dfd12e71cff', 'grab': 'dnd_grab', 'zoom-in': 'zoom_in', 'zoom-out': 'zoom_out',
 'wait': 'watch', 'progress': 'left_ptr_watch half-busy 08e8e1c95fe2fc01f976f1e063a24ccd_',
}

def render(g, k, hot):
    n = 16 * k; px = []
    for y in range(n):
        for x in range(n):
            ch = g[y // k][x // k]
            if ch == '.': px.append(0)
            else:
                r, gg, b = COL[ch]; px.append((255 << 24) | (r << 16) | (gg << 8) | b)
    return n, n, hot[0] * k + (k // 2 if k > 1 else 0) - (0), hot[1] * k + (k // 2 if k > 1 else 0) - 0, px

def escribe_xcursor(ruta, cuadros):
    """cuadros: lista de (size_nominal, w, h, xh, yh, delay, pixels)"""
    n = len(cuadros); ptr = 16 + 12 * n; toc = b''; cuerpo = b''
    for (sz, w, h, xh, yh, delay, px) in cuadros:
        toc += struct.pack('<III', 0xfffd0002, sz, ptr + len(cuerpo))
        cuerpo += struct.pack('<IIIII', 36, 0xfffd0002, sz, 1, 0)[:0]
        cuerpo += struct.pack('<IIIIIIIII', 36, 0xfffd0002, sz, 1, w, h, xh, yh, delay) + struct.pack('<%dI' % len(px), *px)
    open(ruta, 'wb').write(b'Xcur' + struct.pack('<III', 16, 0x10000, n) + toc + cuerpo)

def construir():
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT + '/cursors')
    for nombre, f in BASE.items():
        g, hot = f(); cuadros = []
        for k in (1, 2, 3, 4):
            w, h, xh, yh, px = render(g, k, hot); cuadros.append((16 * k, w, h, xh, yh, 0, px))
        escribe_xcursor(f'{OUT}/cursors/{nombre}', cuadros)
    for nombre, f in ANIM.items():
        cuadros = []
        for k in (2, 3, 4):
            for fr in range(8):
                g, hot = f(fr); w, h, xh, yh, px = render(g, k, hot); cuadros.append((16 * k, w, h, xh, yh, 90, px))
        escribe_xcursor(f'{OUT}/cursors/{nombre}', cuadros)
    for base, nombres in ALIAS.items():
        for a in nombres.split():
            a = a.rstrip('_')
            if a != base and not os.path.exists(f'{OUT}/cursors/{a}'): os.symlink(base, f'{OUT}/cursors/{a}')
    open(f'{OUT}/index.theme', 'w').write('[Icon Theme]\nName=PixelZenCursor\nComment=Cursor pixel art PixelZen\nInherits=breeze_cursors\n')
    return len(os.listdir(OUT + '/cursors'))

if __name__ == '__main__':
    print('cursores:', construir())
