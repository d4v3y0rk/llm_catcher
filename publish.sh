#!/bin/bash

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "Please provide a version number (e.g., ./publish.sh 0.2.3)"
    exit 1
fi

VERSION=$1

# Function to clean up backup files
cleanup_backups() {
    find . -name "*''" -type f -delete
    find . -name "*.tmp" -type f -delete
    find . -name "*.bak" -type f -delete
}

# Initial cleanup of any existing backup files
cleanup_backups

# Check for .pypirc file
PYPIRC="$HOME/.pypirc"
if [ ! -f "$PYPIRC" ]; then
    echo "Error: $PYPIRC not found!"
    echo "Please create $PYPIRC with your PyPI credentials:"
    echo "[pypi]"
    echo "username = __token__"
    echo "password = your-pypi-token"
    exit 1
fi

# Check if .pypirc contains required sections
if ! grep -q "\[pypi\]" "$PYPIRC" || ! grep -q "username" "$PYPIRC" || ! grep -q "password" "$PYPIRC"; then
    echo "Error: $PYPIRC is missing required configuration!"
    echo "Please ensure it contains:"
    echo "[pypi]"
    echo "username = __token__"
    echo "password = your-pypi-token"
    exit 1
fi

# Function to check if command succeeded
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        cleanup_backups  # Clean up on error
        exit 1
    fi
}

# Set up sed command based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: create a temporary file and move it back
    update_version() {
        local file=$1
        local pattern=$2
        sed "s/$pattern/\"$VERSION\"/" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        cleanup_backups  # Clean up after each update
    }
else
    # Linux: use sed -i directly
    update_version() {
        local file=$1
        local pattern=$2
        sed -i "s/$pattern/\"$VERSION\"/" "$file"
        cleanup_backups  # Clean up after each update
    }
fi

echo "Updating version to $VERSION..."

# Update version in pyproject.toml
update_version "pyproject.toml" "version = \".*\""
check_status "Failed to update pyproject.toml"

# Update version in setup.py
update_version "setup.py" "version=\".*\""
check_status "Failed to update setup.py"

# Update version in __init__.py
update_version "llm_catcher/__init__.py" "__version__ = \".*\""
check_status "Failed to update __init__.py"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/
check_status "Failed to clean previous builds"

# Build package
echo "Building package..."
python -m build
check_status "Failed to build package"

# Upload to PyPI
echo "Uploading to PyPI..."
python -m twine upload dist/*
check_status "Failed to upload to PyPI"

echo "Successfully updated version to $VERSION and uploaded to PyPI"

# Optional: Create git tag
read -p "Create git tag v$VERSION? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add pyproject.toml setup.py llm_catcher/__init__.py
    git commit -m "Bump version to $VERSION"
    git tag -a "v$VERSION" -m "Version $VERSION"
    git push && git push --tags
    check_status "Failed to create git tag"
fi