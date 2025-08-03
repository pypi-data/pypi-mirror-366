---
description: Repository Information Overview
alwaysApply: true
---

# GC7 Information

## Summary
GC7 is a Python utility toolkit for PyMoX developers (PY-thon - MO-jo - Flet-X). The project is set up as a Python package that can be published to PyPI using semantic versioning. It uses GitHub Actions for automated releases and follows conventional commits for version management.

## Structure
- **src/gc7/**: Main package source code
- **.github/workflows/**: CI/CD pipeline configurations
- **.venv/**: Python virtual environment
- **.zencoder/**: Configuration for Zencoder

## Language & Runtime
**Language**: Python
**Version**: Python 3.10+
**Build System**: setuptools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- setuptools_scm: For version management
- python-dotenv: For environment variable loading

**Development Dependencies**:
- python-semantic-release: For automated versioning and releases
- build: For building Python packages
- twine: For publishing to PyPI

## Build & Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Build package
python -m build

# Check distribution
twine check dist/* --verbose

# Upload to PyPI
twine upload dist/* --verbose
```

## Version Management
**Tool**: python-semantic-release
**Configuration**: pyproject.toml
**Version Source**: Git tags
**Commands**:
```bash
# Check if a new version would be generated
semantic-release --noop version

# Create a new version locally
semantic-release version --commit --tag --no-push

# Publish a new version
semantic-release publish
```

## CI/CD
**Platform**: GitHub Actions
**Workflow**: .github/workflows/publish.yml
**Trigger**: Push to main branch
**Process**:
1. Checkout code
2. Set up Python 3.10
3. Install dependencies
4. Run semantic-release to version and publish

## Environment Variables
**Required**:
- GH_TOKEN: GitHub token for releases
- PYPI_TOKEN: PyPI token for package publishing

## Project Configuration
**Package Structure**:
- Dynamic versioning using setuptools_scm
- Source code in src/gc7/
- Requires Python 3.10+
- Uses conventional commits for version management
- Current version: v1.1.9 (as of 2025-08-02)
