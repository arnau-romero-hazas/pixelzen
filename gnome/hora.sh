#!/usr/bin/env bash
# PixelZen para GNOME - controla la hora del fondo animado.  hora.sh 21:30 | real | demo
# real = hora del reloj (por defecto) | demo = 24 h en 90 s | HH:MM = congela esa hora
set -euo pipefail
S="$HOME/.local/share/gnome-shell/extensions/pixelzen@mosqui1988.github.io/schemas"
g() { gsettings --schemadir "$S" set org.gnome.shell.extensions.pixelzen "$@"; }
case "${1:-real}" in
  real) g hora-simulada -1; g ciclo-rapido false;;
  demo|ciclo) g hora-simulada -1; g ciclo-rapido true;;
  *) h=${1%%:*}; m=${1##*:}; [ "$h" = "$1" ] && m=0
     [[ "$h" =~ ^[0-9]{1,2}$ && "$m" =~ ^[0-9]{1,2}$ ]] || { echo "uso: hora.sh HH:MM | real | demo" >&2; exit 2; }
     g ciclo-rapido false; g hora-simulada "$(python3 -c "print(int('$h') + int('$m') / 60)")";;
esac
echo "fondo: hora=${1:-real}"
