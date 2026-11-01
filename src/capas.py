#!/usr/bin/env python3
"""PixelZen - monta las capas del fondo animado dia/noche en el plugin de Plasma.
Por cada fase (noche, dorado, dia): cielo RGB, escena RGBA (recorte por diferencia sobre negro/blanco), nubes. Mas sprites sol y luna."""
import os, pickle, struct, subprocess, sys, zlib

RAIZ = os.path.expanduser('~/.local/share/pixelzen')
PLUG = f'{RAIZ}/fondo-animado/com.ruben.pixelzen.wallpaper/contents'
TMP = f'{RAIZ}/fondos/capas'; os.makedirs(TMP, exist_ok=True)
GEN = f'{RAIZ}/src/fondo3.py'
W, H, HOR = 640, 400, 280

def png(ruta, filas, w, h, rgba):
    raw = bytearray()
    for f in filas: raw += b'\x00' + b''.join(bytes(p) for p in f)
    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(ruta, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6 if rgba else 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(bytes(raw), 9)) + ch(b'IEND', b''))

def matte(neg, bla):
    out = []
    for fn, fb in zip(neg, bla):
        fila = []
        for cn, cb in zip(fn, fb):
            a = 1 - sum(cb[i] - cn[i] for i in range(3)) / 765.0
            a = max(0.0, min(1.0, a))
            if a < 0.02: fila.append((0, 0, 0, 0))
            else: fila.append(tuple(min(255, int(cn[i] / a + 0.5)) for i in range(3)) + (int(a * 255 + 0.5),))
        out.append(fila)
    return out

def corre(env, *args):
    e = dict(os.environ, **env)
    subprocess.run([sys.executable, '-I', GEN, *args], env=e, check=True, stdout=subprocess.DEVNULL)

def main():
    os.makedirs(f'{PLUG}/images', exist_ok=True)
    for fase in ('noche', 'dorado', 'dia'):
        print('fase', fase, flush=True)
        corre({'PZ_FASE': fase, 'PZ_SKYONLY': f'{TMP}/cielo-{fase}.pkl'}, TMP, '--anim')
        cielo = pickle.load(open(f'{TMP}/cielo-{fase}.pkl', 'rb'))
        for y in range(HOR, H): cielo[y] = cielo[HOR - 1]
        png(f'{PLUG}/images/cielo-{fase}.png', cielo, W, H, False)
        for modo in ('negro', 'blanco'):
            corre({'PZ_FASE': fase, 'PZ_SKY': modo, 'PZ_DUMP': f'{TMP}/{modo}-{fase}.pkl'}, TMP, '--anim')
        n = pickle.load(open(f'{TMP}/negro-{fase}.pkl', 'rb')); b = pickle.load(open(f'{TMP}/blanco-{fase}.pkl', 'rb'))
        png(f'{PLUG}/images/escena-{fase}.png', matte(n, b), W, H, True)
        os.replace(f'{TMP}/nubes-{fase}.png', f'{PLUG}/images/nubes-{fase}.png')
        if fase == 'noche': os.replace(f'{TMP}/datos.js', f'{PLUG}/ui/datos.js')
    corre({'PZ_SPRITES': f'{TMP}/sprites.pkl'}, TMP, '--anim')
    for nombre, (neg, bla) in pickle.load(open(f'{TMP}/sprites.pkl', 'rb')).items():
        png(f'{PLUG}/images/{nombre}.png', matte(neg, bla), 208, 208, True)
    print('capas listas en', PLUG)

if __name__ == '__main__':
    main()
