#!/usr/bin/env bash
# PixelZen - desinstala: revierte tu configuracion original y borra los temas instalados.
#   ./desinstalar.sh           revierte y borra temas, iconos, cursor, plugins y fuentes
#   ./desinstalar.sh --todo    ademas borra ~/.local/share/pixelzen y ~/.config/pixelzen
set -uo pipefail
R="$HOME/.local/share/pixelzen"; D="$HOME/.local/share"
"$R/revertir.sh"
rm -rf "$D/icons/PixelZen" "$D/icons/PixelZenCursor" "$HOME/.icons/PixelZenCursor" "$D/plasma/desktoptheme/pixelzen" "$D/plasma/wallpapers/com.ruben.pixelzen.wallpaper" \
       "$D/plasma/plasmoids/com.ruben.pixelzen.hud" "$D/plasma/plasmoids/com.ruben.pixelzen.barra" "$D/color-schemes/PixelZen.colors" \
       "$D/aurorae/themes/PixelZen" "$D/konsole/PixelZen.colorscheme" "$D/konsole/PixelZen.profile" "$D/fonts/pixelzen"
fc-cache -f "$D/fonts" >/dev/null 2>&1
if [ "${1:-}" = "--todo" ]; then rm -rf "$HOME/.config/pixelzen"; cp -r "$R/backup" /tmp/pixelzen-backup-final 2>/dev/null; rm -rf "$R"; echo "Borrado todo. Copia de tus ajustes originales en /tmp/pixelzen-backup-final"; fi
echo "PixelZen desinstalado."
