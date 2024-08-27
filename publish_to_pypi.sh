#!/bin/bash

# Ensure the script exits on any error
set -e

# Navigate to the project root directory
cd "$(dirname "$0")"

# Update the version number in setup.py
python update_version.py

# Clean up previous builds
rm -rf dist/

# Build the package
python setup.py sdist bdist_wheel

# Upload the package to PyPI
twine upload dist/*

echo "Package successfully uploaded to PyPI"