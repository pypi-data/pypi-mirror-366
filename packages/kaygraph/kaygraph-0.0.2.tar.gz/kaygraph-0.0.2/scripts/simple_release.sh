#!/usr/bin/env bash
# Simple release script - no BS

set -e

VERSION_TYPE=${1:-patch}

echo "🚀 KayGraph Release"

# Check we're on main
if [ "$(git branch --show-current)" != "main" ]; then
    echo "❌ Not on main branch"
    exit 1
fi

# Run tests
echo "Running tests..."
uv run pytest tests/

# Get version
OLD_VERSION=$(grep -Po '(?<=version = ")[^"]*' pyproject.toml)

# Calculate new version
IFS='.' read -ra PARTS <<< "$OLD_VERSION"
case "$VERSION_TYPE" in
    patch) ((PARTS[2]++));;
    minor) ((PARTS[1]++)); PARTS[2]=0;;
    major) ((PARTS[0]++)); PARTS[1]=0; PARTS[2]=0;;
esac
NEW_VERSION="${PARTS[0]}.${PARTS[1]}.${PARTS[2]}"

echo "Version: $OLD_VERSION → $NEW_VERSION"

# Update versions
sed -i "s/version = \"$OLD_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
sed -i "s/__version__ = \"$OLD_VERSION\"/__version__ = \"$NEW_VERSION\"/" kaygraph/__init__.py

# Commit and tag
git add pyproject.toml kaygraph/__init__.py
git commit -m "bump: version $NEW_VERSION"
git tag "v$NEW_VERSION"

# Build
uv build

echo "✅ Done! Now run:"
echo "  git push origin main --tags"
echo "  uv run twine upload dist/*"