# Simple Release Guide for KayGraph

This is the ACTUAL release process for a Python library. No Docker BS.

## Prerequisites

- `uv` installed
- PyPI account
- Git

## Release Process

### 1. Update Version

Edit `pyproject.toml`:
```toml
version = "0.1.4"  # Change this
```

Edit `kaygraph/__init__.py`:
```python
__version__ = "0.1.4"  # Keep in sync
```

### 2. Update CHANGELOG.md

Add your changes under a new version section.

### 3. Commit and Tag

```bash
git add .
git commit -m "chore: bump version to 0.1.4"
git tag v0.1.4
git push origin main --tags
```

### 4. Build and Publish

```bash
# Build
uv build

# Publish to PyPI
uv run twine upload dist/*
```

That's it. Done.

## For Users

```bash
# Install
pip install kaygraph
# or
uv pip install kaygraph
```

## What You DON'T Need

- Docker
- Kubernetes  
- Complex CI/CD
- 500 config files

KayGraph is ZERO dependency. Keep it simple.