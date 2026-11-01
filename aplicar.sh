#!/usr/bin/env bash
# PixelZen - aplica el tema. Uso: aplicar.sh [todo|colores|plasma|ventanas|fuentes|terminal|iconos|cursor|animado|hud|panel|bloqueo|portable]
# Reversible: ./revertir.sh (hay copia en backup/original/)
set -euo pipefail
R="$HOME/.local/share/pixelzen"; T="$R/tema"; D="$HOME/.local/share"
python3 -I "$R/src/construir.py" >/dev/null
paso="${1:-todo}"

respaldo() { mkdir -p "$R/backup/original"
             for f in kdeglobals kwinrc plasmarc plasmashellrc plasma-org.kde.plasma.desktop-appletsrc konsolerc kcminputrc ksplashrc kscreenlockerrc alacritty/alacritty.toml gtk-3.0/settings.ini gtk-4.0/settings.ini; do
               [ -e "$HOME/.config/$f" ] && [ ! -e "$R/backup/original/$f" ] && { mkdir -p "$R/backup/original/$(dirname "$f")"; cp "$HOME/.config/$f" "$R/backup/original/$f"; }; done; true; }
fuentes_inst() { mkdir -p "$D/fonts/pixelzen"; cp "$R"/fuentes/* "$D/fonts/pixelzen/" 2>/dev/null; fc-cache -f "$D/fonts" >/dev/null 2>&1; true; }
bloqueo()  { kwriteconfig6 --file kscreenlockerrc --group Greeter --key WallpaperPlugin com.ruben.pixelzen.wallpaper
             kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group com.ruben.pixelzen.wallpaper --group General --key Animar true; }

colores()  { mkdir -p "$D/color-schemes"; cp "$T/colores/PixelZen.colors" "$D/color-schemes/"; plasma-apply-colorscheme PixelZen; }
plasma()   { mkdir -p "$D/plasma/desktoptheme"; rm -rf "$D/plasma/desktoptheme/pixelzen"; cp -r "$T/plasma/pixelzen" "$D/plasma/desktoptheme/"; plasma-apply-desktoptheme pixelzen; }
ventanas() { mkdir -p "$D/aurorae/themes"; rm -rf "$D/aurorae/themes/PixelZen"; cp -r "$T/aurorae/PixelZen" "$D/aurorae/themes/"
             kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
             kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__PixelZen
             qdbus6 org.kde.KWin /KWin reconfigure; }
fuentes()  { f="Pixelify Sans,11,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
             for k in font menuFont toolBarFont; do kwriteconfig6 --file kdeglobals --group General --key $k "$f"; done
             kwriteconfig6 --file kdeglobals --group General --key fixed "Departure Mono,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
             kwriteconfig6 --file kdeglobals --group WM --key activeFont "Pixelify Sans,11,-1,5,700,0,0,0,0,0,0,0,0,0,0,1"
             qdbus6 org.kde.KWin /KWin reconfigure; }
panel()    { ln -sfn "$R/hud/com.ruben.pixelzen.barra" "$D/plasma/plasmoids/com.ruben.pixelzen.barra"
             L=$(grep -m1 '^launchers=' "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc" 2>/dev/null | cut -d= -f2-)
             L="${L:-applications:systemsettings.desktop,preferred://filemanager,preferred://browser,applications:org.kde.konsole.desktop}"
             qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$(sed "s|__LANZADORES__|$L|" "$R/src/panel.js")"; }
hud()      { mkdir -p "$D/plasma/plasmoids"; ln -sfn "$R/hud/com.ruben.pixelzen.hud" "$D/plasma/plasmoids/com.ruben.pixelzen.hud"
             qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
               var ds = desktops();
               for (var i = 0; i < ds.length; i++) { var ids = ds[i].widgetIds;
                 for (var j = 0; j < ids.length; j++) { var w = ds[i].widgetById(ids[j]); if (w.type == "com.ruben.pixelzen.hud") w.remove(); } }' >/dev/null
             sleep 2   # esperar a que se libere el hueco; si no, Plasma recoloca el widget. Tamano: se escala con la altura de la pantalla
             qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'var g = screenGeometry(0); var k = Math.max(0.6, Math.min(2, (g.height - 64) / 892)); var w = Math.round(336 * k), h = Math.round(892 * k); desktops()[0].addWidget("com.ruben.pixelzen.hud", Math.max(0, g.width - w - 16), 32, w, h);' >/dev/null; }
iconos()   { python3 -I "$R/src/iconos.py" >/dev/null; mkdir -p "$D/icons"; rm -rf "$D/icons/PixelZen"; cp -r "$T/iconos/PixelZen" "$D/icons/PixelZen"
             kwriteconfig6 --file kdeglobals --group Icons --key Theme PixelZen
             dbus-send --session --type=signal /KIconLoader org.kde.KIconLoader.iconChanged int32:0 2>/dev/null
             dbus-send --session --type=signal /KGlobalSettings org.kde.KGlobalSettings.notifyChange int32:4 int32:0 2>/dev/null; }
cursor()   { python3 -I "$R/src/cursor.py" >/dev/null; mkdir -p "$D/icons" "$HOME/.icons"; rm -rf "$D/icons/PixelZenCursor"; cp -r "$T/cursor/PixelZenCursor" "$D/icons/PixelZenCursor"
             ln -sfn "$D/icons/PixelZenCursor" "$HOME/.icons/PixelZenCursor"   # Plasma solo busca cursores en ~/.icons
             plasma-apply-cursortheme breeze_cursors >/dev/null 2>&1; sleep 1   # fuerza el evento de cambio: si no, KWin no recarga
             plasma-apply-cursortheme PixelZenCursor >/dev/null 2>&1 || kwriteconfig6 --file kcminputrc --group Mouse --key cursorTheme PixelZenCursor; }
animado()  { P="$R/fondo-animado/com.ruben.pixelzen.wallpaper"; mkdir -p "$D/plasma/wallpapers" "$R/fondos/anim"
             python3 -I "$R/src/capas.py" >/dev/null
             ln -sfn "$P" "$D/plasma/wallpapers/com.ruben.pixelzen.wallpaper"
             qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
               var ds = desktops();
               for (var i = 0; i < ds.length; i++) { ds[i].wallpaperPlugin = "com.ruben.pixelzen.wallpaper";
                 ds[i].currentConfigGroup = ["Wallpaper", "com.ruben.pixelzen.wallpaper", "General"]; ds[i].writeConfig("Animar", true); ds[i].writeConfig("Fps", 8); }' >/dev/null; }
fondo()    { plasma-apply-wallpaperimage "$R/fondos/v3.png"; }
terminal() { mkdir -p "$D/konsole"; cp "$T"/konsole/* "$D/konsole/"; command -v alacritty >/dev/null && { mkdir -p "$HOME/.config/alacritty"; cp "$T/alacritty/alacritty.toml" "$HOME/.config/alacritty/alacritty.toml"; }
             kwriteconfig6 --file konsolerc --group "Desktop Entry" --key DefaultProfile PixelZen.profile
             command -v fish >/dev/null && { mkdir -p "$HOME/.config/fish/conf.d"; cp "$R/src/pixelzen.fish" "$HOME/.config/fish/conf.d/pixelzen.fish"; }; true; }

portable() { fuentes_inst; python3 -I "$R/src/iconos.py" >/dev/null; mkdir -p "$D/icons"; rm -rf "$D/icons/PixelZen"; cp -r "$T/iconos/PixelZen" "$D/icons/PixelZen"
             python3 -I "$R/src/cursor.py" >/dev/null; rm -rf "$D/icons/PixelZenCursor"; cp -r "$T/cursor/PixelZenCursor" "$D/icons/PixelZenCursor"
             mkdir -p "$HOME/.icons"; ln -sfn "$D/icons/PixelZenCursor" "$HOME/.icons/PixelZenCursor"; }   # sin tocar ajustes de Plasma

if [ "$paso" = todo ]; then respaldo; fuentes_inst; colores; plasma; ventanas; fuentes; terminal; iconos; cursor; animado; hud; panel; bloqueo; else respaldo; "$paso"; fi
if [ "$paso" = portable ]; then echo "PixelZen: iconos, cursor y fuentes instalados (no se ha tocado ningun ajuste)."
else echo "PixelZen: paso '$paso' aplicado. Para volver atras: $R/revertir.sh"; fi
