#!/usr/bin/env bash
# PixelZen - instalador. Solo toca tu usuario (sin sudo). Uso:
#   ./instalar.sh                    instala y aplica el tema completo (KDE Plasma 6)
#   ./instalar.sh --grafico          lo mismo, con ventanas de KDE (es lo que hace el doble clic)
#   ./instalar.sh --portable         solo iconos, cursor y fuentes, para otros escritorios (experimental)
#   ./instalar.sh --sin-aplicar      solo copia y genera los recursos
#   ./instalar.sh --casa=39.5,-0.4,"Mi ciudad"   fija tu ubicacion (si no, se usa la zona horaria)
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"; DEST="$HOME/.local/share/pixelzen"; APLICAR=1; CASA=""; GRAFICO=0; PORTABLE=0
for a in "$@"; do case "$a" in
  --sin-aplicar) APLICAR=0;; --casa=*) CASA="${a#--casa=}";; --grafico) GRAFICO=1;; --portable) PORTABLE=1;;
  -h|--help) sed -n 2,8p "$0"; exit 0;; esac; done
[ "$GRAFICO" = 1 ] && ! command -v kdialog >/dev/null && GRAFICO=0

dialogo() { # dialogo TIPO TEXTO  (TIPO: msgbox | error | yesno)
  if [ "$GRAFICO" = 1 ]; then case "$1" in msgbox) kdialog --title PixelZen --msgbox "$2";; error) kdialog --title PixelZen --error "$2";; yesno) kdialog --title PixelZen --yes-label Instalar --no-label Cancelar --yesno "$2";; esac
  else echo "$2"; fi; }
fallo() { dialogo error "$1"; exit 1; }

plasma6() { local v; v="$(plasmashell --version 2>/dev/null | awk '{print $2}')"; [ "${v%%.*}" -ge 6 ] 2>/dev/null; }

if [ "$PORTABLE" = 1 ]; then need=(python3 fc-cache); else need=(python3 qdbus6 kwriteconfig6 plasmashell fc-cache); fi
falta=(); for c in "${need[@]}"; do command -v "$c" >/dev/null || falta+=("$c"); done
if [ "$PORTABLE" = 0 ] && [ "$APLICAR" = 1 ]; then
  if ! plasma6; then
    fallo "PixelZen completo necesita KDE Plasma 6 y no lo detecto en este equipo, asi que no he tocado nada.

Si usas otro escritorio puedes instalar solo las piezas portables (iconos, cursor y fuentes) con:
./instalar.sh --portable"
  fi
fi
if [ ${#falta[@]} -gt 0 ]; then
  [ "$APLICAR" = 1 ] && fallo "Faltan: ${falta[*]}. Instalalos con el gestor de paquetes de tu distribucion y vuelve a probar."
  echo "Aviso: faltan ${falta[*]}"
fi

if [ "$GRAFICO" = 1 ]; then
  if [ "$PORTABLE" = 1 ]; then txt="Se instalaran los iconos, el cursor y las fuentes de PixelZen."
  else txt="Se instalara el tema PixelZen: fondo animado, panel de datos, iconos, cursor y ventanas.

Antes guarda una copia de tus ajustes y se puede deshacer. No usa sudo. Tarda alrededor de un minuto y el escritorio se recargara."; fi
  dialogo yesno "$txt" || exit 0
fi

principal() {
  echo "==> Copiando a $DEST"
  mkdir -p "$DEST"
  for x in src hud fondo-animado fuentes vendor licencias aplicar.sh revertir.sh desinstalar.sh LEEME.md; do rm -rf "${DEST:?}/$x"; cp -a "$AQUI/$x" "$DEST/$x"; done
  chmod +x "$DEST"/*.sh "$DEST"/src/*.sh 2>/dev/null || true
  if [ -n "$CASA" ]; then
    IFS=',' read -r lat lon nombre <<<"$CASA"; tz="$(timedatectl show -p Timezone --value 2>/dev/null || echo '')"
    mkdir -p "$HOME/.config/pixelzen"
    printf '{\n  "casa": {"nombre": "%s", "lat": %s, "lon": %s, "tz": "%s"}\n}\n' "${nombre:-casa}" "$lat" "$lon" "$tz" > "$HOME/.config/pixelzen/ubicacion.json"
    echo "==> Ubicacion de casa guardada en ~/.config/pixelzen/ubicacion.json"
  fi
  if [ "$PORTABLE" = 1 ]; then
    echo "==> Instalando iconos, cursor y fuentes"; "$DEST/aplicar.sh" portable
  elif [ "$APLICAR" = 1 ]; then
    echo "==> Generando y aplicando el tema (tarda ~1 min)"; "$DEST/aplicar.sh" todo
    echo "==> Reiniciando el shell de Plasma"; systemctl --user restart plasma-plasmashell.service 2>/dev/null || true
  else
    echo "Copiado. Aplica cuando quieras con: $DEST/aplicar.sh todo"
  fi
}

if [ "$GRAFICO" = 1 ]; then
  LOG="$(mktemp /tmp/pixelzen-instalar.XXXXXX)"
  kdialog --title PixelZen --passivepopup "Instalando PixelZen... tarda alrededor de un minuto." 10 2>/dev/null &
  set +e; ( set -e; principal ) >"$LOG" 2>&1; rc=$?; set -e
  [ $rc -eq 0 ] || fallo "No se ha podido instalar. Tus ajustes originales no se han perdido.

$(tail -n 6 "$LOG")

Registro completo: $LOG"
  if [ "$PORTABLE" = 1 ]; then dialogo msgbox "Listo. Elige 'PixelZen' como tema de iconos y 'PixelZenCursor' como cursor en los ajustes de tu escritorio."
  else dialogo msgbox "Listo. Para volver atras: $DEST/revertir.sh"; fi
else
  principal
  if [ "$PORTABLE" = 1 ]; then echo "Listo. Elige 'PixelZen' (iconos) y 'PixelZenCursor' (cursor) en los ajustes de tu escritorio."
  elif [ "$APLICAR" = 1 ]; then echo "Listo. Para volver atras: $DEST/revertir.sh   |   desinstalar todo: $DEST/desinstalar.sh"; fi
fi
