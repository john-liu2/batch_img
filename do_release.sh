#!/bin/bash
set -e

echo "Building clean release..."
cp -p pyproject.toml pyproject_dev.toml
cp -p pyproject_prod.toml pyproject.toml
rm -rf dist/ *.egg-info
cp -p batch_img/config.json batch_img/config_dev.json
cp -p batch_img/config_prod.json batch_img/config.json

python -m build

mv pyproject_dev.toml pyproject.toml
mv batch_img/config_dev.json batch_img/config.json
cp -p dist/batch_img*.tar.gz ~/Downloads/
echo "Build complete: ll dist/*"
