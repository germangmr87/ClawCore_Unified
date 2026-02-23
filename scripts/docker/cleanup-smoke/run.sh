#!/usr/bin/env bash
set -euo pipefail

cd /repo

export CLAWCORE_STATE_DIR="/tmp/clawcore-test"
export CLAWCORE_CONFIG_PATH="${CLAWCORE_STATE_DIR}/clawcore.json"

echo "==> Build"
pnpm build

echo "==> Seed state"
mkdir -p "${CLAWCORE_STATE_DIR}/credentials"
mkdir -p "${CLAWCORE_STATE_DIR}/agents/main/sessions"
echo '{}' >"${CLAWCORE_CONFIG_PATH}"
echo 'creds' >"${CLAWCORE_STATE_DIR}/credentials/marker.txt"
echo 'session' >"${CLAWCORE_STATE_DIR}/agents/main/sessions/sessions.json"

echo "==> Reset (config+creds+sessions)"
pnpm clawcore reset --scope config+creds+sessions --yes --non-interactive

test ! -f "${CLAWCORE_CONFIG_PATH}"
test ! -d "${CLAWCORE_STATE_DIR}/credentials"
test ! -d "${CLAWCORE_STATE_DIR}/agents/main/sessions"

echo "==> Recreate minimal config"
mkdir -p "${CLAWCORE_STATE_DIR}/credentials"
echo '{}' >"${CLAWCORE_CONFIG_PATH}"

echo "==> Uninstall (state only)"
pnpm clawcore uninstall --state --yes --non-interactive

test ! -d "${CLAWCORE_STATE_DIR}"

echo "OK"
