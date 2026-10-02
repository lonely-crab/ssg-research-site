#!/usr/bin/env bash
# Откат: public_html.prev -> public_html
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${HELIOS_HOST:-helios.cs.ifmo.ru}"
PORT="${HELIOS_PORT:-2222}"
USER="${HELIOS_USER:-s336402}"
KEY="${HELIOS_SSH_KEY:-$ROOT/deploy/helios_key}"
KNOWN_HOSTS="${KNOWN_HOSTS:-$ROOT/deploy/known_hosts}"
REMOTE_ROOT="${HELIOS_REMOTE_ROOT:-public_html}"

ssh_cmd=(ssh -p "$PORT" -o StrictHostKeyChecking=yes)
if [[ -f "$KNOWN_HOSTS" ]]; then
  ssh_cmd+=(-o UserKnownHostsFile="$KNOWN_HOSTS")
fi
if [[ -n "${HELIOS_PASSWORD:-}" ]]; then
  export SSHPASS="$HELIOS_PASSWORD"
  ssh_cmd=(sshpass -e -P "assword" "${ssh_cmd[@]}"
    -o PreferredAuthentications=keyboard-interactive,password
    -o KbdInteractiveAuthentication=yes
    -o PubkeyAuthentication=no
    -o NumberOfPasswordPrompts=1)
elif [[ -f "$KEY" ]]; then
  ssh_cmd+=(-i "$KEY" -o IdentitiesOnly=yes)
fi

"${ssh_cmd[@]}" "$USER@$HOST" "set -e
test -d ${REMOTE_ROOT}.prev
rm -rf ${REMOTE_ROOT}.bad
if [ -d $REMOTE_ROOT ]; then mv $REMOTE_ROOT ${REMOTE_ROOT}.bad; fi
mv ${REMOTE_ROOT}.prev $REMOTE_ROOT
echo rollback ok
"
