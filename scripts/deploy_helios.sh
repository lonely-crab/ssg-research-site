#!/usr/bin/env bash
# Выкладка site/ на Helios: tar по ssh (на FreeBSD часто нет rsync).
# Пароль — HELIOS_PASSWORD, ключ — HELIOS_SSH_KEY / deploy/helios_key.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE_DIR="${SITE_DIR:-$ROOT/site}"
HOST="${HELIOS_HOST:-helios.cs.ifmo.ru}"
PORT="${HELIOS_PORT:-2222}"
USER="${HELIOS_USER:-s336402}"
KEY="${HELIOS_SSH_KEY:-$ROOT/deploy/helios_key}"
KNOWN_HOSTS="${KNOWN_HOSTS:-$ROOT/deploy/known_hosts}"
REMOTE_ROOT="${HELIOS_REMOTE_ROOT:-public_html}"
SITE_URL="${HELIOS_SITE_URL:-https://se.ifmo.ru/~s336402/}"

if [[ ! -d "$SITE_DIR" || ! -f "$SITE_DIR/index.html" ]]; then
  echo "нет сборки: $SITE_DIR/index.html (сначала SITE_URL=$SITE_URL make build)" >&2
  exit 1
fi

ssh_cmd=(ssh -p "$PORT" -o StrictHostKeyChecking=yes)
if [[ -f "$KNOWN_HOSTS" ]]; then
  ssh_cmd+=(-o UserKnownHostsFile="$KNOWN_HOSTS")
fi
if [[ -n "${HELIOS_PASSWORD:-}" ]]; then
  export SSHPASS="$HELIOS_PASSWORD"
  ssh_cmd=(sshpass -e "${ssh_cmd[@]}" -o PreferredAuthentications=password -o PubkeyAuthentication=no)
elif [[ -f "$KEY" ]]; then
  ssh_cmd+=(-i "$KEY" -o IdentitiesOnly=yes)
fi

remote="$USER@$HOST"
echo "деплой $SITE_DIR -> $remote:$REMOTE_ROOT"

"${ssh_cmd[@]}" "$remote" "set -e
if [ -d $REMOTE_ROOT ]; then
  rm -rf ${REMOTE_ROOT}.prev
  mv $REMOTE_ROOT ${REMOTE_ROOT}.prev
fi
mkdir -p $REMOTE_ROOT
"

tar_cmd=(tar)
if tar --disable-copyfile -cf - -C /dev/null . >/dev/null 2>&1; then
  tar_cmd+=(--disable-copyfile --no-xattrs)
fi
"${tar_cmd[@]}" -cf - -C "$SITE_DIR" . | gzip -c | "${ssh_cmd[@]}" "$remote" "gzip -dc | tar -xf - -C $REMOTE_ROOT"

echo "healthcheck $SITE_URL"
sleep 2
code="$(curl -sS -o /tmp/helios_index.html -w '%{http_code}' -L --max-time 20 "$SITE_URL")"
if [[ "$code" != "200" ]]; then
  echo "ожидал HTTP 200, получил $code" >&2
  exit 1
fi
if ! grep -q "Задержка" /tmp/helios_index.html; then
  echo "в HTML нет контрольной строки" >&2
  exit 1
fi
echo "ok $code $SITE_URL"
