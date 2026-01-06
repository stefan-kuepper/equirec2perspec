#!/usr/bin/env bash
set -euo pipefail

echo "Building package..."
uv build

echo "Checking package with twine..."
uv run twine check dist/*

echo "Build completed successfully!"
echo "Artifacts are in dist/"
