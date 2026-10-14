#!/usr/bin/env bash
set -euo pipefail

OPTIONS=/data/options.json
KEY_FILE=/data/encryption_key

# Schluessel fuer die im DB gespeicherten Controller-Zugangsdaten, einmalig erzeugt.
# Geht er verloren, muss der Controller in der Web-UI neu eingetragen werden.
if [ ! -s "$KEY_FILE" ]; then
    echo "[unifi_toolkit] Erzeuge ENCRYPTION_KEY in $KEY_FILE"
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > "$KEY_FILE"
    chmod 600 "$KEY_FILE"
fi

export ENCRYPTION_KEY_FILE="$KEY_FILE"
export DATABASE_URL="sqlite+aiosqlite:////data/unifi_toolkit.db"
# Authentifizierung uebernimmt Home Assistant (Ingress)
export DEPLOYMENT_TYPE=local
export APP_PORT=8000
LOG_LEVEL="$(jq -r '.log_level // "info"' "$OPTIONS" | tr '[:lower:]' '[:upper:]')"
STALKER_REFRESH_INTERVAL="$(jq -r '.stalker_refresh_interval // 60' "$OPTIONS")"
export LOG_LEVEL STALKER_REFRESH_INTERVAL

# Standardsprache der Oberflaeche; im Browser per Einstellungen umschaltbar
LANGUAGE="$(jq -r '.language // "de"' "$OPTIONS")"
echo "window.HA_I18N_DEFAULT = \"${LANGUAGE}\";" > /etc/nginx/ha-i18n/config.js

cd /app
nginx -g 'daemon off;' &
NGINX_PID=$!
python run.py &
APP_PID=$!

stop_children() {
    kill -TERM "$NGINX_PID" "$APP_PID" 2>/dev/null || true
    wait "$NGINX_PID" "$APP_PID" 2>/dev/null || true
}
trap 'stop_children; exit 0' TERM INT

# Stirbt einer der beiden Prozesse, wird der andere sauber beendet und der
# Container endet; der Supervisor-Watchdog startet ihn neu
set +e
wait -n "$NGINX_PID" "$APP_PID"
rc=$?
stop_children
exit "$rc"
