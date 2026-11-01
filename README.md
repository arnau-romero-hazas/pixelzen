# PixelZen

> Tema de escritorio para **KDE Plasma 6** en pixel art: paisaje japonés animado que sigue al sol de tu ciudad, panel de datos, iconos y cursor a juego.
> Artículo con capturas y cómo está hecho: **https://ralcaniz.dev/posts/pixelzen-escritorio-kde-pixel-art/**

**Instalación rápida:** descarga `pixelzen-1.0.tar.gz` desde [Releases](../../releases), descomprímelo y haz doble clic en **«Instalar PixelZen»** (o ejecuta `./instalar.sh`).

SHA-256 del paquete 1.0: `d11705d136cf5e91ca4bc23061971ad66b7fe0ab895d3a112123022c729d89ba`

Licencia: GPL-3.0-or-later (código y arte). Las fuentes y los glifos de iconos mantienen sus propias licencias, en `licencias/`.

Un tema de escritorio completo para **KDE Plasma 6** con estética de **Japón antiguo en pixel art**:
paisaje animado que sigue el sol de tu ciudad, ventanas, iconos y cursor pixel, una barra mínima y un
HUD con datos del sistema, de la red y de desarrollo. Todo se genera con **Python puro** (sin dependencias).

## Qué incluye

| Pieza | Qué es |
|---|---|
| Fondo animado | Plugin de Plasma. Sol y luna recorren el cielo según tu hora y ubicación; el paisaje pasa de noche a hora dorada y a día. Estrellas, nubes, farolillos, pétalos, luciérnagas, grullas y estrellas fugaces. También en la pantalla de bloqueo. |
| HUD | Widget con reloj (calendario japonés y fase lunar), sistema, red y puertos, desarrollo, herramientas y haiku. Solo lectura, sin red, sin `sudo`. |
| Ventanas | Decoración Aurorae con marco pixel y botones cuadrados. |
| Panel | Barra superior mínima: inicio, apps, reloj, bandeja reducida. |
| Iconos | ~3000 iconos pixel (glifos Pixelarticons + azulejos, carpetas y hojas propias). Lo no cubierto cae a Breeze. |
| Cursor | Cursor Xcursor pixel con punta roja de torii. |
| Terminal | Alacritty y Konsole, prompt de fish a juego. |
| Tipografía | Departure Mono (datos y terminal), Pixelify Sans (interfaz), DotGothic16 (kanji). |

## Requisitos

KDE Plasma 6 (Wayland o X11), `python3`, `qdbus6`, `kwriteconfig6`, `fc-cache`. Alacritty y fish son opcionales.

## Instalar

**Lo más fácil (2 clics):** descomprime el paquete, haz **doble clic en «Instalar PixelZen»** y pulsa *Instalar*.
Se encarga de todo y avisa cuando termina.

**Desde la terminal:**

```bash
tar xzf pixelzen-1.0.tar.gz && cd pixelzen-1.0
./instalar.sh                                   # usa tu zona horaria para el sol
./instalar.sh --casa=39.5,-0.4,"Mi ciudad"      # o fija tu ubicación
```

**Si no usas KDE Plasma 6:** el tema completo no funciona (el fondo animado y el HUD son componentes de Plasma),
pero puedes instalar solo las piezas estándar: `./instalar.sh --portable` (iconos, cursor y fuentes; experimental,
sin probar fuera de Plasma). Después elige `PixelZen` y `PixelZenCursor` en los ajustes de tu escritorio.

Solo toca tu usuario, nunca usa `sudo`. Antes de cambiar nada guarda una copia de tus ajustes en
`~/.local/share/pixelzen/backup/original/`.

## Uso

```bash
~/.local/share/pixelzen/src/hora.sh 21:30   # congela la hora del fondo
~/.local/share/pixelzen/src/hora.sh demo    # 24 h en 90 s para ver anochecer
~/.local/share/pixelzen/src/hora.sh real    # vuelve a la hora del reloj

~/.local/share/pixelzen/aplicar.sh iconos   # reaplica una sola parte
# pasos: todo colores plasma ventanas fuentes terminal iconos cursor animado hud panel bloqueo
```

La ubicación se calcula **sin red**: tu zona horaria (`zone1970.tab`) o la `casa` de
`~/.config/pixelzen/ubicacion.json`. Con `~/.config/pixelzen/demo` el HUD muestra datos ficticios (útil para capturas).

## Deshacer

```bash
~/.local/share/pixelzen/revertir.sh         # vuelve a tu configuración anterior
~/.local/share/pixelzen/desinstalar.sh      # además borra los temas (--todo borra también el proyecto)
```

## Cómo está hecho

- `src/fondo3.py` dibuja el paisaje (640×400, ampliado ×3) con paletas por fase; `src/capas.py` separa cielo y
  escena con un recorte por diferencia de fondo (sobre negro y sobre blanco) y crea los sprites del sol y la luna.
- El plugin QML (`fondo-animado/`) mezcla las tres iluminaciones según la altura del sol, calculada con la
  posición solar de la NOAA, y anima las capas a 8 fps.
- `src/iconos.py` traduce ~3000 nombres de icono de KDE a glifos pixel; `src/cursor.py` escribe el formato Xcursor a mano.
- `src/construir.py` genera el esquema de colores, el tema de Plasma (marcos pixel en SVG), las ventanas y las terminales.
- `hud/` contiene los plasmoides QML y `datos.py`, el motor de datos.

## Licencias

Código y arte generado: GPL-3.0-or-later (`licencias/GPL-3.0.txt`). Fuentes: SIL OFL 1.1 (Departure Mono,
Pixelify Sans, DotGothic16, VT323). Glifos: Pixelarticons, MIT (© Gerrit Halfmann). Textos en `licencias/`.
