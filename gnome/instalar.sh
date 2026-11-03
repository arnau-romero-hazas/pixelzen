#!/usr/bin/env bash
# PixelZen para GNOME (Ubuntu 24.04+): fondo animado que sigue al sol + panel de datos.
#   ./instalar.sh                                instala la extension (ubicacion por zona horaria)
#   ./instalar.sh --casa=39.5,-0.4,"Mi ciudad"   fija tu ubicacion
#   ./instalar.sh --sin-fondo                    no cambia el fondo estatico de GNOME
# Solo toca tu usuario, nunca usa sudo. Para deshacer: ./desinstalar.sh
set -euo pipefail

UUID="pixelzen@mosqui1988.github.io"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
EXT="$HOME/.local/share/gnome-shell/extensions/$UUID"
CFG="$HOME/.config/pixelzen"
CASA=""; FONDO=1
for a in "$@"; do case "$a" in
  --casa=*) CASA="${a#--casa=}";;
  --sin-fondo) FONDO=0;;
  -h|--help) sed -n 2,6p "$0"; exit 0;;
  *) echo "opcion desconocida: $a" >&2; exit 2;;
esac; done

for c in gnome-shell python3 glib-compile-schemas gsettings fc-cache; do
  command -v "$c" >/dev/null || { echo "Falta '$c'. PixelZen para GNOME necesita GNOME Shell 46 o superior." >&2; exit 1; }
done
ver="$(gnome-shell --version | grep -oE '[0-9]+' | head -1)"
[ "${ver:-0}" -ge 46 ] || { echo "GNOME Shell $ver no soportado (minimo 46)." >&2; exit 1; }

echo "==> Copiando la extension a $EXT"
rm -rf "$EXT"; mkdir -p "$EXT/code"
cp -a "$AQUI/$UUID/." "$EXT/"
cp "$RAIZ/fondo-animado/com.ruben.pixelzen.wallpaper/contents/code/ubicacion.py" "$EXT/code/"
cp "$RAIZ/hud/com.ruben.pixelzen.hud/contents/code/datos.py" "$EXT/code/"
cp "$RAIZ/LICENSE" "$EXT/"

echo "==> Dibujando el paisaje (Python puro, tarda alrededor de un minuto)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 -I "$AQUI/construir.py" "$EXT" "$TMP"
glib-compile-schemas "$EXT/schemas"

echo "==> Instalando fuentes pixel"
mkdir -p "$HOME/.local/share/fonts/pixelzen"
cp "$RAIZ"/fuentes/*.{otf,ttf} "$HOME/.local/share/fonts/pixelzen/"
fc-cache -f "$HOME/.local/share/fonts/pixelzen" >/dev/null

if [ -n "$CASA" ]; then
  IFS=',' read -r lat lon nombre <<<"$CASA"; tz="$(timedatectl show -p Timezone --value 2>/dev/null || echo '')"
  mkdir -p "$CFG"
  printf '{\n  "casa": {"nombre": "%s", "lat": %s, "lon": %s, "tz": "%s"}\n}\n' "${nombre:-casa}" "$lat" "$lon" "$tz" > "$CFG/ubicacion.json"
  echo "==> Ubicacion de casa guardada en $CFG/ubicacion.json"
fi

if [ "$FONDO" = 1 ]; then
  echo "==> Fondo estatico de GNOME (se ve en Actividades y en la pantalla de bloqueo)"
  mkdir -p "$CFG" "$HOME/.local/share/backgrounds"
  if [ ! -f "$CFG/gnome-fondo-anterior" ]; then
    { echo "picture-uri=$(gsettings get org.gnome.desktop.background picture-uri)"
      echo "picture-uri-dark=$(gsettings get org.gnome.desktop.background picture-uri-dark)"
      echo "picture-options=$(gsettings get org.gnome.desktop.background picture-options)"
      echo "screensaver-picture-uri=$(gsettings get org.gnome.desktop.screensaver picture-uri)"
    } > "$CFG/gnome-fondo-anterior"
  fi
  cp "$EXT/fondo.png" "$HOME/.local/share/backgrounds/pixelzen.png"
  uri="file://$HOME/.local/share/backgrounds/pixelzen.png"
  gsettings set org.gnome.desktop.background picture-uri "$uri"
  gsettings set org.gnome.desktop.background picture-uri-dark "$uri"
  gsettings set org.gnome.desktop.background picture-options zoom
  gsettings set org.gnome.desktop.screensaver picture-uri "$uri"
fi

echo "==> Activando la extension"
if ! gnome-extensions enable "$UUID" 2>/dev/null; then
  # GNOME aun no conoce la extension (se descubre al reiniciar el shell): se marca como activa
  python3 -I - <<EOF
import ast, subprocess
cur = subprocess.run(['gsettings', 'get', 'org.gnome.shell', 'enabled-extensions'], capture_output=True, text=True).stdout.strip()
l = ast.literal_eval(cur.replace('@as ', '')) if cur else []
if '$UUID' not in l:
    l.append('$UUID')
    subprocess.run(['gsettings', 'set', 'org.gnome.shell', 'enabled-extensions', str(l)], check=True)
EOF
fi
[ "$(gsettings get org.gnome.shell disable-user-extensions)" = true ] && \
  echo "AVISO: tienes desactivadas las extensiones de usuario. Activalas en la app Extensiones."

echo
echo "Listo. Falta reiniciar GNOME Shell para que cargue la extension:"
if [ "${XDG_SESSION_TYPE:-}" = x11 ]; then
  echo "  pulsa Alt+F2, escribe r y pulsa Intro (no se cierra ninguna ventana)."
else
  echo "  cierra sesion y vuelve a entrar (en Wayland no se puede reiniciar el shell en caliente)."
fi
echo "Hora del fondo: $AQUI/hora.sh 21:30 | demo | real"
