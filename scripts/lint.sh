#!/usr/bin/env bash
set -euo pipefail

echo "Running ruff check..."
uv run ruff check

echo "Running ruff format check..."
uv run ruff format --check

echo "Running mypy type checking..."
uv run mypy src/equirec2perspec

echo "All lint checks passed!"
