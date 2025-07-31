# PyPI Release Guide for machofile

This guide provides step-by-step instructions for releasing new versions of machofile to PyPI.

## Prerequisites

- Python 3.7+ installed
- Virtual environment with build tools
- PyPI account and API token
- Git repository with main branch updated

## Step 1: Environment Setup

```bash
# Activate your virtual environment
source ../machofile-dev/venv/bin/activate

# Ensure build tools are installed
pip install --upgrade build twine
```

## Step 2: Update Version Numbers

**Important**: Update version numbers in both files:

### Update `__init__.py`
```python
__version__ = "2025.07.31"  # Change to new version
```

### Update `pyproject.toml`
```toml
version = "2025.07.31"  # Change to new version
```

### Update `CITATION.cff`
```yaml
version: "2025.07.31"  # Change to new version
date-released: 2025-07-31  # Update release date
```

## Step 3: Clean Previous Builds

```bash
# Remove previous build artifacts
rm -rf dist/ build/ machofile.egg-info/
```

## Step 4: Build the Package

```bash
# Build both source distribution and wheel
python -m build
```

**Expected output**: Should create `dist/machofile-<version>.tar.gz` and `dist/machofile-<version>-py3-none-any.whl`

## Step 5: Test Package Locally

```bash
# Install the built package locally
pip install dist/machofile-<version>-py3-none-any.whl

# Test import
python -c "import machofile; print(f'Version: {machofile.__version__}')"

# Test command-line interface
machofile --help

# Uninstall for clean state
pip uninstall machofile -y
```

## Step 6: Validate Package with Twine

```bash
# Check package validity
twine check dist/*
```

**Expected output**: `PASSED` for both files

## Step 7: Upload to PyPI

### Option A: Direct Upload to PyPI (Recommended for stable releases)

```bash
# Upload to PyPI
twine upload dist/*
```

### Option B: Test on TestPyPI First (For testing)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ machofile
```

## Step 8: Verify Upload

```bash
# Wait a few minutes for PyPI to process
sleep 60

# Test installation from PyPI
pip install machofile

# Verify functionality
python -c "import machofile; print(f'Installed version: {machofile.__version__}')"
machofile --help
```

## Step 9: Update Repository

```bash
# Commit version changes
git add .
git commit -m "Release version 2025.07.31"
git push origin main

# Create a release tag
git tag -a v2025.07.31 -m "Release version 2025.07.31"
git push origin v2025.07.31
```

## Step 10: Update Documentation

- Update the PyPI URL in `CITATION.cff` if needed
- Update any version references in documentation
- Create a GitHub release with release notes

## Troubleshooting

### Build Errors
- Ensure all required files are present (`__init__.py`, `pyproject.toml`, etc.)
- Check for syntax errors in Python files
- Verify version numbers match across all files

### Upload Errors
- **403 Forbidden**: Check API token in `~/.pypirc`
- **409 Conflict**: Version already exists - increment version number
- **Network errors**: Check internet connection and PyPI status

### Import Errors After Installation
- Verify `__init__.py` imports are correct
- Check that `__all__` list includes all public classes
- Ensure `main` function is imported for CLI functionality

## File Structure Check

Before building, ensure these files are present:
```
machofile/
├── __init__.py          # Package initialization
├── machofile.py         # Main module
├── pyproject.toml       # Build configuration
├── MANIFEST.in          # Include additional files
├── README.md            # Package description
├── LICENSE              # MIT license
├── API_documentation_machofile.md
└── CITATION.cff         # Citation information
```

## Version Numbering

Follow semantic versioning:
- **Major.Minor.Patch** (e.g., 2025.07.31)
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

## Security Notes

- Never commit API tokens to version control
- Use `~/.pypirc` for storing credentials
- Test packages thoroughly before release
- Consider using TestPyPI for major changes

## Quick Release Checklist

- [ ] Version numbers updated in all files
- [ ] Code tested locally
- [ ] Package builds successfully
- [ ] Twine validation passes
- [ ] Upload to PyPI successful
- [ ] Installation from PyPI works
- [ ] Git tag created and pushed
- [ ] Documentation updated 