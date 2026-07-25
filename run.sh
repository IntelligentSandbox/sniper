#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

if [[ -f .env ]]; then
    source .env
fi

if [[ -z "${SMEE_URL:-}" ]]; then
    echo "Set SMEE_URL in .env"
    exit 1
fi

if ! command -v smee >/dev/null; then
    echo "Install Smee before running Sniper"
    exit 1
fi

smee -u "$SMEE_URL" --path /webhook --port 4000 &
smee_pid=$!

cleanup() {
    kill "$smee_pid" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

mix run --no-halt
