#!/usr/bin/env python3
"""PixelZen para GNOME - genera las capas del fondo animado dentro de la extension.
Reutiliza tal cual src/capas.py y src/fondo3.py del proyecto (Python puro, sin dependencias).
Uso: construir.py <carpeta_de_la_extension> <carpeta_temporal>"""
import json, os, shutil, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, 'src'))
import capas  # noqa: E402

def main():
    ext, tmp = sys.argv[1], sys.argv[2]
    plug = os.path.join(tmp, 'plug')
    os.makedirs(os.path.join(plug, 'ui'), exist_ok=True)
    capas.PLUG = plug
    capas.TMP = os.path.join(tmp, 'capas'); os.makedirs(capas.TMP, exist_ok=True)
    capas.GEN = os.path.join(RAIZ, 'src', 'fondo3.py')
    capas.main()

    # imagenes y datos de la escena (datos.js de Plasma -> datos.json)
    dst = os.path.join(ext, 'images')
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(plug, 'images'), dst)
    js = open(os.path.join(plug, 'ui', 'datos.js')).read()
    datos = json.loads(js[js.index('{'):js.rindex('}') + 1])
    json.dump(datos, open(os.path.join(ext, 'datos.json'), 'w'))

    # fondo estatico (lo usa GNOME en la vista de actividades y en la pantalla de bloqueo)
    subprocess.run([sys.executable, '-I', capas.GEN, os.path.join(tmp, 'v3')], check=True, stdout=subprocess.DEVNULL)
    shutil.copy(os.path.join(tmp, 'v3', 'v3.png'), os.path.join(ext, 'fondo.png'))
    print('capas listas en', ext)

if __name__ == '__main__':
    main()
