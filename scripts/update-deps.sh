#!/usr/bin/env bash
set -euo pipefail

echo "Updating dependencies..."
uv lock --upgrade

echo "Syncing environment..."
uv sync

echo "Dependencies updated!"
