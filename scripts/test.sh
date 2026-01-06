#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-}"
COVERAGE="${COVERAGE:-false}"

if [[ -n "$PYTHON_VERSION" ]]; then
    echo "Installing Python $PYTHON_VERSION..."
    uv python install "$PYTHON_VERSION"
    echo "Syncing dependencies for Python $PYTHON_VERSION..."
    uv sync --python "$PYTHON_VERSION"
else
    echo "Syncing dependencies..."
    uv sync
fi

echo "Verifying package imports..."
uv run python -c "from equirec2perspec import Equirectangular; print('Import successful')"

echo "Running tests..."
if [[ "$COVERAGE" == "true" ]]; then
    uv run pytest --cov=src/equirec2perspec --cov-report=xml --cov-report=term-missing
else
    uv run pytest
fi

echo "All tests passed!"
