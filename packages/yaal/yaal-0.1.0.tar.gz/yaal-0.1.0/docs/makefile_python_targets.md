# Makefile Python Build and Upload Targets

This document describes the new Python package build and upload targets added to the main Makefile.

## New Targets Added

### `python-build`
**Purpose**: Build Python package for distribution

**What it does**:
1. 🧹 **Cleans previous builds** - Removes `dist/`, `build/`, and `*.egg-info/` directories
2. 🔨 **Builds package with uv** - Uses `uv build` to create both wheel and source distribution
3. 📋 **Shows package contents** - Lists the generated files in `dist/` directory
4. ✅ **Confirms completion** - Provides success feedback

**Usage**:
```bash
make python-build
```

**Output**:
- Creates `dist/yaal_parser-0.1.0-py3-none-any.whl` (wheel package)
- Creates `dist/yaal_parser-0.1.0.tar.gz` (source distribution)

### `python-upload`
**Purpose**: Upload Python package to PyPI

**What it does**:
1. 📦 **Depends on python-build** - Automatically builds package first
2. ⚠️ **Credential warning** - Reminds user to set up PyPI credentials
3. 📤 **Uploads to PyPI** - Uses `uv publish` to upload both wheel and source distribution
4. ✅ **Confirms completion** - Provides success feedback

**Usage**:
```bash
make python-upload
```

**Prerequisites**:
- PyPI account and API token configured
- Proper authentication setup for `uv publish`

## Integration with Existing Makefile

### Updated `.PHONY` Declaration
Added `python-build` and `python-upload` to the `.PHONY` targets list.

### Enhanced Help Output
The `make help` command now includes:
```
  python-build        - Build Python package for distribution
  python-upload       - Upload Python package to PyPI
```

### Updated Usage Examples
Added to the usage section:
```
  make python-build      # Build Python package
  make python-upload     # Upload to PyPI
```

### Enhanced Status Command
The `make status` command now includes a new section:
```
Python Package:
  Location: src/yaal_parser/
  Status: ✅ Ready for distribution
  Build: make python-build
  Upload: make python-upload
```

### Enhanced Clean Target
The `make clean` command now also removes:
- `dist/` - Distribution packages
- `*.egg-info/` - Package metadata
- `.venv` - Virtual environment (root level)
- `htmlcov` - Coverage reports (root level)

## Workflow Examples

### Development Workflow
```bash
# 1. Make changes to the code
# 2. Test the changes
make python-test-basic

# 3. Build the package
make python-build

# 4. Test the built package locally
uv run yaal --version
uv run yaal parse examples/01_basic_features.yaal
```

### Release Workflow
```bash
# 1. Update version in pyproject.toml
# 2. Run full test suite
make python-test

# 3. Build and upload to PyPI
make python-upload
```

### Clean Development Environment
```bash
# Clean all build artifacts
make clean

# Start fresh
make python-env
make python-test-basic
```

## Package Contents

The built package includes:
- ✅ **Core Python package** (`src/yaal_parser/`)
- ✅ **CLI tool** (`yaal` command)
- ✅ **Documentation** (`docs/` directory)
- ✅ **Examples** (`examples/` directory with 12 YAAL files)
- ✅ **Tests** (unit and integration tests)
- ✅ **C++ implementation** (for reference and comparison)
- ✅ **Build system files** (CMake, Makefiles)

## Dependencies and Requirements

### Build Dependencies
- `uv` - Modern Python package manager and build tool
- Python >= 3.8.1

### Runtime Dependencies
- `lark >= 1.1.0` - Parser generator library

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatter
- `isort` - Import sorter
- `flake8` - Linter
- `mypy` - Type checker

## Error Handling

### Common Issues and Solutions

**Issue**: `uv build` fails
**Solution**: Ensure `pyproject.toml` is properly configured and all dependencies are available

**Issue**: `uv publish` fails with authentication error
**Solution**: Set up PyPI API token:
```bash
# Configure PyPI token
uv publish --token YOUR_API_TOKEN

# Or set up in environment
export UV_PUBLISH_TOKEN=YOUR_API_TOKEN
```

**Issue**: Package build includes unwanted files
**Solution**: Update `.gitignore` or add exclusions to `pyproject.toml`

## Integration Benefits

### Unified Build System
- **Single Makefile** controls both C++ and Python builds
- **Consistent commands** across different components
- **Integrated testing** for both implementations

### Development Efficiency
- **One-command builds** - `make python-build`
- **Automated cleanup** - `make clean` handles all artifacts
- **Status overview** - `make status` shows complete project state

### Release Management
- **Automated workflow** - Build and upload in one command
- **Dependency management** - uv handles all Python dependencies
- **Version consistency** - Single source of truth in `pyproject.toml`

## Future Enhancements

### Planned Improvements
- 📋 **Version bumping** - Automated version increment targets
- 📋 **Test PyPI upload** - Target for testing uploads
- 📋 **Release notes** - Automated changelog generation
- 📋 **CI/CD integration** - GitHub Actions workflow

### Possible Extensions
- 📋 **Docker builds** - Container packaging targets
- 📋 **Documentation builds** - Sphinx documentation generation
- 📋 **Performance testing** - Benchmark targets
- 📋 **Security scanning** - Vulnerability check targets

## Summary

The new `python-build` and `python-upload` targets provide:

1. ✅ **Complete Python packaging workflow**
2. ✅ **Integration with existing build system**
3. ✅ **Modern tooling** (uv-based)
4. ✅ **Comprehensive package contents**
5. ✅ **Developer-friendly commands**
6. ✅ **Production-ready distribution**

The YAAL parser project now has a professional Python packaging workflow that integrates seamlessly with the existing C++ build system, providing a unified development and release experience.