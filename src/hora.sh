#!/usr/bin/env bash
# PixelZen - controla la hora del fondo animado.  hora.sh 21:30 | real | demo
# real = hora del reloj (por defecto) | demo = 24 h en 90 s | HH:MM = congela esa hora
case "${1:-real}" in
  real) val=-1; demo=false;;
  demo|ciclo) val=-1; demo=true;;
  *) h=${1%%:*}; m=${1##*:}; [ "$h" = "$1" ] && m=0; val=$(python3 -c "print(int('$h') + int('$m') / 60)"); demo=false;;
esac
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
  var ds = desktops();
  for (var i = 0; i < ds.length; i++) { ds[i].currentConfigGroup = ['Wallpaper', 'com.ruben.pixelzen.wallpaper', 'General'];
    ds[i].writeConfig('HoraSimulada', $val); ds[i].writeConfig('CicloRapido', $demo); ds[i].reloadConfig(['Wallpaper', 'com.ruben.pixelzen.wallpaper', 'General']); }" >/dev/null
echo "fondo: hora=${1:-real}"
