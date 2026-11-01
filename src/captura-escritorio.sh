#!/usr/bin/env bash
# Captura SOLO el escritorio (fondo + widgets + panel) usando un escritorio virtual vacio temporal.
# Asi nunca sale ninguna ventana tuya. Uso: captura-escritorio.sh salida.png
set -u
OUT="${1:-/tmp/escritorio.png}"
M=org.kde.KWin.VirtualDesktopManager; V=(org.kde.KWin /VirtualDesktopManager)
n0=$(qdbus6 "${V[@]}" $M.count)
qdbus6 "${V[@]}" $M.createDesktop "$n0" pzvacio >/dev/null; sleep 1
[ "$(qdbus6 "${V[@]}" $M.count)" = "$((n0 + 1))" ] || { echo "no se pudo crear el escritorio"; exit 1; }
qdbus6 org.kde.KWin /KWin org.kde.KWin.setCurrentDesktop "$((n0 + 1))" >/dev/null; sleep 3
[ "$(qdbus6 org.kde.KWin /KWin org.kde.KWin.currentDesktop)" = "$((n0 + 1))" ] && spectacle ${PZ_PUNTERO:+-p} -b -n -f -o "$OUT" >/dev/null 2>&1
qdbus6 org.kde.KWin /KWin org.kde.KWin.setCurrentDesktop 1 >/dev/null; sleep 1
id=$(qdbus6 --literal "${V[@]}" org.freedesktop.DBus.Properties.Get $M desktops | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | tail -1)
qdbus6 "${V[@]}" $M.removeDesktop "$id" >/dev/null
echo "escritorios: $(qdbus6 "${V[@]}" $M.count)  captura: $OUT"
