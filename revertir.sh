#!/usr/bin/env bash
# PixelZen - vuelve al estado anterior (backup/original). No borra el tema instalado ni las fuentes.
set -uo pipefail
R="$HOME/.local/share/pixelzen"; B="$R/backup/original"; C="$HOME/.config"
for f in kdeglobals kwinrc kscreenlockerrc plasmarc plasmashellrc plasma-org.kde.plasma.desktop-appletsrc konsolerc kcminputrc ksplashrc alacritty/alacritty.toml gtk-3.0/settings.ini gtk-4.0/settings.ini; do
  [ -e "$B/$f" ] && cp "$B/$f" "$C/$f"
done
rm -f "$HOME/.config/fish/conf.d/pixelzen.fish"
[ -e "$B/kscreenlockerrc" ] || kwriteconfig6 --file kscreenlockerrc --group Greeter --key WallpaperPlugin --delete 2>/dev/null
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'var ds=desktops(); for (var i=0;i<ds.length;i++){var ids=ds[i].widgetIds; for (var j=0;j<ids.length;j++){var w=ds[i].widgetById(ids[j]); if (w.type=="com.ruben.pixelzen.hud") w.remove();}}' >/dev/null 2>&1
ct=$(kreadconfig6 --file "$B/kcminputrc" --group Mouse --key cursorTheme 2>/dev/null); plasma-apply-cursortheme "${ct:-breeze_cursors}" >/dev/null 2>&1
esq=$(kreadconfig6 --file kdeglobals --group General --key ColorScheme); [ -n "$esq" ] && plasma-apply-colorscheme "$esq" >/dev/null 2>&1
tema=$(kreadconfig6 --file plasmarc --group Theme --key name); plasma-apply-desktoptheme "${tema:-default}" >/dev/null 2>&1
qdbus6 org.kde.KWin /KWin reconfigure
systemctl --user restart plasma-plasmashell.service 2>/dev/null || (kquitapp6 plasmashell; sleep 1; kstart plasmashell >/dev/null 2>&1 &)
echo "PixelZen revertido. Reinicia sesion si algo se ve a medias."
