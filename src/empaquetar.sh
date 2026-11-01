#!/usr/bin/env bash
# PixelZen - crea dist/pixelzen-VERSION.tar.gz (sin copias de seguridad, descargas ni recursos generados).
set -euo pipefail
R="$HOME/.local/share/pixelzen"; V="${1:-1.0}"; mkdir -p "$R/dist"
tar -C "$R" -czf "$R/dist/pixelzen-$V.tar.gz" --transform "s,^\.,pixelzen-$V," \
  --exclude=./backup --exclude=./descargas --exclude=./fondos --exclude=./tema --exclude=./dist --exclude=./blog \
  --exclude='*.bak' --exclude='*.pre-dia.bak' --exclude='__pycache__' --exclude='*/contents/images/*' --exclude='*/contents/ui/datos.js' .
( cd "$R/dist" && sha256sum "pixelzen-$V.tar.gz" > "pixelzen-$V.tar.gz.sha256" )
ls -la "$R/dist" | awk 'NR>1{print $5, $9}'
