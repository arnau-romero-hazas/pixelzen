#!/usr/bin/env python3
"""PixelZen - construye todo el tema en ~/.local/share/pixelzen/tema/ (sin tocar el sistema).
aplicar.sh lo copia a su sitio. Python puro."""
import gzip, json, os, shutil, sys

RAIZ = os.path.expanduser('~/.local/share/pixelzen/tema')
P = dict(bg='#0a0c24', bg2='#11143a', alt='#171a42', btn='#1b1e4a', borde='#6a4a8a', borde_off='#2b2850',
         linea='#3a2f6a', texto='#f3e9d2', dim='#9a94b8', rojo='#c8382e', rosa='#e0837f', ambar='#e0b36a',
         verde='#7fb88a', rosa_flor='#f2b8c6', violeta='#8a4a79', neg='#e0524a', azul='#7a7fd8',
         magenta='#c77fb0', cian='#7fc4c4')

def rgb(h): h = h.lstrip('#'); return ','.join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))
def escribe(ruta, txt, gz=False):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    if gz:
        with gzip.open(ruta, 'wb') as f: f.write(txt.encode())
    else:
        open(ruta, 'w').write(txt)

# ---------------------------------------------------------------- marcos SVG de pixeles
def grupo(id_, filas, y0, col):
    """filas: lista de strings; col: {caracter: (hex, opacidad)}. Une tramos horizontales."""
    h, w = len(filas), len(filas[0]); out = [f'<g id="{id_}" transform="translate(0,{y0})">',
                                             f'<rect width="{w}" height="{h}" fill="#000" fill-opacity="0"/>']
    for y, fila in enumerate(filas):
        x = 0
        while x < w:
            c = fila[x]
            if c == '.': x += 1; continue
            x2 = x
            while x2 < w and fila[x2] == c: x2 += 1
            hexc, op = col[c]
            out.append(f'<rect x="{x}" y="{y}" width="{x2 - x}" height="{h and 1}" fill="{hexc}" fill-opacity="{op}"/>')
            x = x2
    out.append('</g>'); return '\n'.join(out), h

def marco(prefijos, trozos, col, margenes, ancho=40):
    """trozos: nombre -> filas. Se apilan en vertical; las pistas (hint-*) van a la derecha."""
    cuerpo, y = [], 0
    for pre in prefijos:
        for nombre, filas in trozos.items():
            g, h = grupo(pre + nombre, filas, y, col); cuerpo.append(g); y += h + 1
        mt, mb, ml, mr = margenes
        for n, (w, h) in dict(top=(1, mt), bottom=(1, mb), left=(ml, 1), right=(mr, 1)).items():
            if w and h: cuerpo.append(f'<rect id="{pre}hint-{n}-margin" x="{ancho - 10}" y="{y}" width="{w}" height="{h}" fill="#f0f" fill-opacity="0"/>'); y += 1 + h
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{y + 1}" '
            f'viewBox="0 0 {ancho} {y + 1}" shape-rendering="crispEdges">\n' + '\n'.join(cuerpo) + '\n</svg>\n')

def trozos_plasma(acento=False):
    a = 'a' if acento else 'b'
    return {
        'topleft':     [f'..{a}{a}{a}', '.bfff', 'bffff', 'bffff', 'bffff'],
        'top':         ['bbbbb', 'fffff', 'fffff', 'fffff', 'fffff'],
        'topright':    ['bbb..', 'fffb.', 'ffffb', 'ffffb', 'ffffb'],
        'left':        ['bffff'] * 5, 'center': ['fffff'] * 5, 'right': ['ffffb'] * 5,
        'bottomleft':  ['bffff', 'bffff', 'bffff', '.bfff', '..bbb'],
        'bottom':      ['fffff', 'fffff', 'fffff', 'fffff', 'bbbbb'],
        'bottomright': ['ffffb', 'ffffb', 'ffffb', 'fffb.', 'bbb..'],
    }

def tema_plasma():
    d = os.path.join(RAIZ, 'plasma/pixelzen')
    def col(alpha, borde=P['borde'], acento=P['rojo']): return {'f': (P['bg'], alpha), 'b': (borde, 1), 'a': (acento, 1)}
    # panel: casi solo borde; translucido
    escribe(f'{d}/widgets/panel-background.svgz', marco(['', 'floating-'], trozos_plasma(), col(0.80), (1, 1, 1, 1)), True)
    escribe(f'{d}/widgets/tooltip.svgz', marco([''], trozos_plasma(True), col(0.94), (5, 5, 5, 5)), True)
    escribe(f'{d}/widgets/background.svgz', marco([''], trozos_plasma(True), col(0.88), (5, 5, 5, 5)), True)
    escribe(f'{d}/widgets/translucentbackground.svgz', marco([''], trozos_plasma(True), col(0.62), (5, 5, 5, 5)), True)
    escribe(f'{d}/dialogs/background.svgz', marco([''], trozos_plasma(True), col(0.94), (6, 6, 6, 6)), True)
    escribe(f'{d}/colors', esquema('PixelZen', completo=False))
    escribe(f'{d}/metadata.json', json.dumps({'KPackageStructure': 'Plasma/Theme', 'KPlugin': {
        'Id': 'pixelzen', 'Name': 'PixelZen', 'Description': 'Japon antiguo en pixel art, zen',
        'Authors': [{'Name': 'Ruben'}], 'Category': 'Plasma Theme', 'License': 'GPL-2.0+', 'Version': '1.0'}}, indent=2))

# ---------------------------------------------------------------- esquema de colores
def esquema(nombre, completo=True):
    def sec(n, bgn, bga, fgn, fgi=None, deco=P['rosa']):
        return (f'[Colors:{n}]\nBackgroundAlternate={rgb(bga)}\nBackgroundNormal={rgb(bgn)}\nDecorationFocus={rgb(deco)}\n'
                f'DecorationHover={rgb(P["rosa"])}\nForegroundActive={rgb(P["ambar"])}\nForegroundInactive={rgb(fgi or P["dim"])}\n'
                f'ForegroundLink={rgb(P["rosa"])}\nForegroundNegative={rgb(P["neg"])}\nForegroundNeutral={rgb(P["ambar"])}\n'
                f'ForegroundNormal={rgb(fgn)}\nForegroundPositive={rgb(P["verde"])}\nForegroundVisited={rgb(P["magenta"])}\n\n')
    s = ''
    s += ('[ColorEffects:Disabled]\nColor=56,56,56\nColorAmount=0\nColorEffect=0\nContrastAmount=0.65\nContrastEffect=1\n'
          'IntensityAmount=0.1\nIntensityEffect=2\n\n[ColorEffects:Inactive]\nChangeSelectionColor=true\nColor=112,111,110\n'
          'ColorAmount=0.025\nColorEffect=2\nContrastAmount=0.1\nContrastEffect=2\nEnable=false\nIntensityAmount=0\nIntensityEffect=0\n\n')
    s += sec('Button', P['btn'], P['alt'], P['texto'])
    s += sec('Complementary', P['bg'], P['alt'], P['texto'])
    s += sec('Header', P['bg'], P['alt'], P['texto'])
    s += '[Colors:Header][Inactive]\nBackgroundNormal=' + rgb(P['bg']) + '\n\n'
    s += sec('Selection', P['violeta'], P['rojo'], P['texto'], P['texto'], P['rosa']).replace(
        'ForegroundActive=' + rgb(P['ambar']), 'ForegroundActive=' + rgb(P['texto']))
    s += sec('Tooltip', P['bg'], P['alt'], P['texto'])
    s += sec('View', P['bg2'], P['alt'], P['texto'])
    s += sec('Window', P['bg'], P['alt'], P['texto'])
    if completo:
        s += (f'[General]\nColorScheme={nombre}\nName={nombre}\nshadeSortColumn=true\n\n[KDE]\ncontrast=4\n\n'
              f'[WM]\nactiveBackground={rgb(P["bg"])}\nactiveBlend={rgb(P["texto"])}\nactiveForeground={rgb(P["texto"])}\n'
              f'inactiveBackground={rgb("#07081a")}\ninactiveBlend={rgb(P["dim"])}\ninactiveForeground={rgb(P["dim"])}\n')
    return s

# ---------------------------------------------------------------- ventanas (Aurorae)
def aurorae():
    d = os.path.join(RAIZ, 'aurorae/PixelZen')
    TOP = 28; N = TOP
    BAY = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    def grad(y, x, activo=True):
        t = max(0.0, 1 - (y - 1) / 11.0) * 0.95
        return 'p' if activo and (BAY[y % 4][x % 4] + 0.5) / 16 < t else 'f'
    def deco(pre, borde, acento, relleno, linea, activo=True):
        c = {'f': (relleno, 0.96), 'p': ('#1d2160', 0.96), 'b': (borde, 1), 'l': (linea, 1), 'a': (acento, 1)}
        tl = ['.b'] + [('ba' if 4 <= i < 22 else 'b' + grad(i, 3, activo)) for i in range(1, N - 1)] + ['bl']
        tr = ['b.'] + [grad(i, 0, activo) + 'b' for i in range(1, N - 1)] + ['lb']
        top = ['bbbb'] + [''.join(grad(i, x, activo) for x in range(4)) for i in range(1, N - 1)] + ['llll']
        return {pre + 'topleft': tl, pre + 'top': top, pre + 'topright': tr,
                pre + 'left': ['bf'] * 4, pre + 'center': ['f' * 4] * 4, pre + 'right': ['fb'] * 4,
                pre + 'bottomleft': ['bf', '.b'], pre + 'bottom': ['ffff', 'bbbb'], pre + 'bottomright': ['fb', 'b.']}, c
    cuerpo, y = [], 0
    for pre, borde, acento, linea, act in (('decoration-', P['borde'], P['rojo'], P['linea'], True),
                                           ('decoration-inactive-', P['borde_off'], P['borde_off'], '#1b1e4a', False)):
        trozos, c = deco(pre, borde, acento, P['bg'], linea, act)
        for n, filas in trozos.items():
            g, h = grupo(n, filas, y, c); cuerpo.append(g); y += h + 1
    escribe(f'{d}/decoration.svg', f'<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="12" height="{y}" '
                                   f'viewBox="0 0 12 {y}" shape-rendering="crispEdges">\n' + '\n'.join(cuerpo) + '\n</svg>\n')
    # botones 18x18 con cuadrado de 12x12 de esquinas muescadas
    cuad = ['..' + 'x' * 8 + '..'] + ['.' + 'x' * 10 + '.'] + ['x' * 12] * 8 + ['.' + 'x' * 10 + '.'] + ['..' + 'x' * 8 + '..']
    def glifo(nombre):
        g = set()
        if nombre == 'close':    g = {(3 + i, 3 + i) for i in range(6)} | {(3 + i, 8 - i) for i in range(6)}
        elif nombre == 'minimize': g = {(3 + i, 8) for i in range(6)}
        elif nombre == 'maximize': g = {(3 + i, 3) for i in range(6)} | {(3 + i, 8) for i in range(6)} | {(3, 3 + j) for j in range(6)} | {(8, 3 + j) for j in range(6)}
        elif nombre == 'restore':  g = ({(3 + i, 5) for i in range(5)} | {(3 + i, 9) for i in range(5)} | {(3, 5 + j) for j in range(5)} | {(7, 5 + j) for j in range(5)}
                                        | {(5 + i, 3) for i in range(5)} | {(9, 3 + j) for j in range(3)})
        elif nombre == 'keepabove': g = {(5, 4), (6, 4), (4, 5), (7, 5), (3, 6), (8, 6)}
        elif nombre == 'keepbelow': g = {(3, 5), (8, 5), (4, 6), (7, 6), (5, 7), (6, 7)}
        elif nombre == 'shade':    g = {(3 + i, 3) for i in range(6)} | {(3 + i, 4) for i in range(6)}
        else:                      g = {(5, 5), (6, 5), (5, 6), (6, 6)}
        return g
    base = dict(close=P['rojo'], minimize=P['ambar'], maximize=P['verde'], restore=P['verde'])
    for nombre in ('close', 'minimize', 'maximize', 'restore', 'alldesktops', 'keepabove', 'keepbelow', 'shade', 'help'):
        b = base.get(nombre, P['violeta'])
        estados = {'active': (b, None), 'hover': (b, P['bg']), 'pressed': (P['violeta'] if nombre != 'close' else '#8a2420', P['texto']),
                   'inactive': (P['borde_off'], None), 'deactivated': (P['borde_off'], None), 'hover-inactive': (b, P['bg'])}
        cuerpo = []
        for i, (est, (cb, cg)) in enumerate(estados.items()):
            y0 = i * 18; filas = []
            cb = cb if est != 'hover' else {'close': '#e0524a', 'minimize': '#f0c97e', 'maximize': '#9fd4a8'}.get(nombre, '#b0609a')
            for yy in range(12):
                fila = ''
                for xx in range(12):
                    if cuad[yy][xx] != 'x': fila += '.'
                    elif cg and (xx, yy) in glifo(nombre): fila += 'g'
                    else: fila += 'c'
                filas.append('.' * 3 + fila + '.' * 3)
            filas = ['.' * 18] * 3 + filas + ['.' * 18] * 3
            g, _ = grupo(f'{est}-center', filas, y0, {'c': (cb, 1), 'g': (cg or '#000', 1)}); cuerpo.append(g)
        escribe(f'{d}/{nombre}.svg', f'<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="18" height="{18 * len(estados)}" '
                                     f'viewBox="0 0 18 {18 * len(estados)}" shape-rendering="crispEdges">\n' + '\n'.join(cuerpo) + '\n</svg>\n')
    escribe(f'{d}/PixelZenrc', f'''[General]
ActiveTextColor={rgb(P['texto'])}
InactiveTextColor={rgb(P['dim'])}
Animation=false
AnimationTime=0

[Layout]
BorderLeft=2
BorderRight=2
BorderBottom=2
TitleEdgeTop=2
TitleEdgeBottom=2
TitleEdgeLeft=2
TitleEdgeRight=2
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=0
TitleEdgeRightMaximized=0
TitleHeight=24
TitleBorderLeft=8
TitleBorderRight=8
TitleAlignment=Left
TitleVerticalAlignment=Center
ButtonWidth=18
ButtonHeight=18
ButtonSpacing=4
ButtonMarginTop=3
ButtonMarginTopMaximized=3
PaddingTop=0
PaddingBottom=0
PaddingLeft=0
PaddingRight=0
ExplicitButtonSpacer=0
''')
    escribe(f'{d}/metadata.desktop', '[Desktop Entry]\nName=PixelZen\nComment=Ventanas pixel, Japon antiguo\n'
            'Type=Service\nX-KDE-PluginInfo-Name=PixelZen\nX-KDE-PluginInfo-Version=1.0\nX-KDE-PluginInfo-License=GPL\n')

# ---------------------------------------------------------------- terminales
def terminales():
    escribe(f'{RAIZ}/alacritty/alacritty.toml', f'''# PixelZen - generado por src/construir.py
[general]
working_directory = "None"
live_config_reload = true

[env]
TERM = "xterm-256color"

[window]
dimensions = {{ columns = 100, lines = 30 }}
padding = {{ x = 14, y = 12 }}
dynamic_padding = true
decorations = "Full"
opacity = 0.90
title = "Alacritty@CachyOS"
decorations_theme_variant = "Dark"

[scrolling]
history = 10000
multiplier = 3

[font]
normal = {{ family = "Departure Mono", style = "Regular" }}
bold = {{ family = "Departure Mono", style = "Regular" }}
italic = {{ family = "Departure Mono", style = "Regular" }}
bold_italic = {{ family = "Departure Mono", style = "Regular" }}
size = 11.5
builtin_box_drawing = true

[cursor]
style = {{ shape = "Block", blinking = "On" }}
blink_interval = 600
unfocused_hollow = true

[colors]
draw_bold_text_with_bright_colors = false
[colors.primary]
background = "{P['bg']}"
foreground = "{P['texto']}"
[colors.cursor]
text = "{P['bg']}"
cursor = "{P['rojo']}"
[colors.selection]
text = "{P['texto']}"
background = "{P['violeta']}"
[colors.normal]
black = "{P['btn']}"
red = "{P['neg']}"
green = "{P['verde']}"
yellow = "{P['ambar']}"
blue = "{P['azul']}"
magenta = "{P['magenta']}"
cyan = "{P['cian']}"
white = "#d8cfb8"
[colors.bright]
black = "#4a4478"
red = "#f0705f"
green = "#9fd4a8"
yellow = "#f0c97e"
blue = "#9aa0f0"
magenta = "#e09ac8"
cyan = "#9fe0e0"
white = "{P['texto']}"
''')
    cs = ['[General]\nDescription=PixelZen\nOpacity=0.92\nWallpaper=\n']
    nombres = [('Background', P['bg']), ('Foreground', P['texto']), ('Color0', P['btn']), ('Color1', P['neg']), ('Color2', P['verde']),
               ('Color3', P['ambar']), ('Color4', P['azul']), ('Color5', P['magenta']), ('Color6', P['cian']), ('Color7', '#d8cfb8'),
               ('Color0Intense', '#4a4478'), ('Color1Intense', '#f0705f'), ('Color2Intense', '#9fd4a8'), ('Color3Intense', '#f0c97e'),
               ('Color4Intense', '#9aa0f0'), ('Color5Intense', '#e09ac8'), ('Color6Intense', '#9fe0e0'), ('Color7Intense', P['texto'])]
    for n, c in nombres: cs.append(f'\n[{n}]\nColor={rgb(c)}')
    escribe(f'{RAIZ}/konsole/PixelZen.colorscheme', ''.join(cs) + '\n')
    escribe(f'{RAIZ}/konsole/PixelZen.profile', '[Appearance]\nColorScheme=PixelZen\nFont=Departure Mono,11,-1,5,400,0,0,0,0,0,0,0,0,0,0,1\n\n'
            '[General]\nName=PixelZen\nParent=FALLBACK/\n\n[Scrolling]\nHistorySize=10000\n')

if __name__ == '__main__':
    for sub in ('plasma', 'aurorae', 'colores', 'alacritty', 'konsole'): shutil.rmtree(f'{RAIZ}/{sub}', ignore_errors=True)
    escribe(f'{RAIZ}/colores/PixelZen.colors', esquema('PixelZen'))
    tema_plasma(); aurorae(); terminales()
    print('construido en', RAIZ)
