#!/usr/bin/env bash
# PixelZen para GNOME - quita la extension, las fuentes y devuelve tu fondo anterior.
set -uo pipefail
UUID="pixelzen@mosqui1988.github.io"
EXT="$HOME/.local/share/gnome-shell/extensions/$UUID"
CFG="$HOME/.config/pixelzen"

gnome-extensions disable "$UUID" 2>/dev/null
python3 -I - <<EOF
import ast, subprocess
cur = subprocess.run(['gsettings', 'get', 'org.gnome.shell', 'enabled-extensions'], capture_output=True, text=True).stdout.strip()
l = ast.literal_eval(cur.replace('@as ', '')) if cur else []
if '$UUID' in l:
    l.remove('$UUID')
    subprocess.run(['gsettings', 'set', 'org.gnome.shell', 'enabled-extensions', str(l)], check=True)
EOF
rm -rf "$EXT"
rm -rf "$HOME/.local/share/fonts/pixelzen"; fc-cache -f >/dev/null 2>&1

if [ -f "$CFG/gnome-fondo-anterior" ]; then
  while IFS='=' read -r clave valor; do
    esquema=org.gnome.desktop.background
    [ "$clave" = screensaver-picture-uri ] && { esquema=org.gnome.desktop.screensaver; clave=picture-uri; }
    gsettings set "$esquema" "$clave" "$valor"
  done < "$CFG/gnome-fondo-anterior"
  rm -f "$CFG/gnome-fondo-anterior"
  echo "Fondo anterior restaurado."
fi
rm -f "$HOME/.local/share/backgrounds/pixelzen.png"
echo "PixelZen para GNOME desinstalado. (Tu ~/.config/pixelzen/ubicacion.json se conserva si existe.)"
