#!/bin/bash
set -e

echo "Building clean release..."
cp -p pyproject.toml pyproject_dev.toml
cp -p pyproject_release.toml pyproject.toml
rm -rf dist/ *.egg-info

python -m build

mv pyproject_dev.toml pyproject.toml
echo "Build complete: ll dist/*"
