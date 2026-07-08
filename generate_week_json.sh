#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"

PROMPT="Mirate el README, el formato de ejemplo dentro de src/content/news y el prompt definido en scripts/generate_week.py. Con todo eso toma el ultimo week-xx.csv que se encuentra en este directorio raiz y genera el correspondiente .json dentro de src/content/news"

log() {
  echo "[generate_week_json] $1"
}

LATEST_CSV=$(ls -1 week-*.csv 2>/dev/null | sort -V | tail -n1)
if [ -z "$LATEST_CSV" ]; then
  log "No se encontro ningun week-xx.csv en la raiz del repo."
  exit 0
fi
log "CSV detectado: $LATEST_CSV"
log "Ejecutando claude para generar el JSON (esto puede tardar varios minutos)..."

# Heartbeat en background para dar feedback mientras claude trabaja.
(
  while true; do
    sleep 20
    log "Sigue trabajando, por favor espera..."
  done
) &
HEARTBEAT_PID=$!

cleanup() {
  kill "$HEARTBEAT_PID" 2>/dev/null || true
  wait "$HEARTBEAT_PID" 2>/dev/null || true
}
trap cleanup EXIT
trap 'log "Cancelado por el usuario."; exit 0' INT TERM

claude -p "$PROMPT" --permission-mode acceptEdits --verbose
STATUS=$?

if [ $STATUS -ne 0 ]; then
  log "claude finalizo con codigo $STATUS. Revisa src/content/news para confirmar si el JSON se genero."
else
  log "Listo. JSON generado en src/content/news."
fi

exit 0
