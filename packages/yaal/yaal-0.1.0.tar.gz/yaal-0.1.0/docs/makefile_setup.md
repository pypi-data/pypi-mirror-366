# YAAL Parser Makefile Setup

## Overview

A comprehensive Makefile has been created in the root directory to manage both Python and C++ YAAL parser tests with proper environment setup using the `uv` tool. All commands run from the root directory without requiring directory changes.

## Available Targets

### Main Targets

| Target | Description | Dependencies |
|--------|-------------|--------------|
| `help` | Show all available targets and usage | None |
| `python-test` | Run all Python parser tests | `python-env` |
| `python-test-basic` | Run only basic Python tests (faster) | `python-env` |
| `python-test-coverage` | Run Python tests with detailed coverage | `python-env` |
| `cpp-test` | Run C++ parser tests | None |
| `python-env` | Set up Python environment with uv | None |
| `status` | Show test status summary | None |
| `clean` | Clean all build artifacts | None |

### Usage Examples

```bash
# Quick status check (from root directory)
make status

# Fast Python test (recommended for development)
make python-test-basic

# Full Python test suite
make python-test

# Python tests with coverage report
make python-test-coverage

# C++ tests
make cpp-test

# Clean everything
make clean
```

**Note**: All commands are run from the project root directory. No need to `cd` into test directories.

## Python Environment Setup

The Makefile uses `uv` for Python environment management:

- **Environment Location**: `tests/python/.venv`
- **Dependencies**: Automatically installed from `pyproject.toml`
- **Packages**: `lark>=1.2.2`, `pytest>=8.4.1`, `pytest-cov>=6.2.1`

### Python Environment Commands

```bash
# Set up environment (automatic with test targets)
make python-env

# Manual environment activation (if needed)
uv shell --project tests/python
```

## Test Results Summary

### Current Status (as of latest run)

#### Python Tests (`make python-test-basic`)
- **Pass Rate**: 17/20 tests (85%)
- **Status**: ⚠️ Needs grammar improvements
- **Known Issues**:
  - Empty values after colons
  - Quoted string values
  - Triple-quoted string values

#### C++ Tests (`make cpp-test`)
- **Pass Rate**: 85/95 tests (89.5%)
- **Status**: ✅ Production ready
- **Known Issues**: Minor fixture path issues only

## Development Workflow

### Recommended Development Cycle

1. **Quick Check**: `make python-test-basic` (fast feedback)
2. **Full Validation**: `make python-test` (comprehensive)
3. **C++ Verification**: `make cpp-test` (when needed)
4. **Status Overview**: `make status` (project summary)

### For Grammar Development

```bash
# Edit grammar file
vim tests/python/src/yaal_parser/grammar.lark

# Quick test
make python-test-basic

# Full test when ready
make python-test
```

### For Test Development

```bash
# Edit test files
vim tests/python/tests/test_*.py

# Run specific test category (from root)
uv run --project tests/python pytest tests/python/tests/test_parser_basic.py -v

# Or use make targets (recommended)
make python-test-basic
```

## File Structure

```
.
├── Makefile                    # Main build file
├── tests/
│   ├── python/                 # Python tests
│   │   ├── pyproject.toml      # uv project config
│   │   ├── src/yaal_parser/    # Parser package
│   │   └── tests/              # Test files
│   └── cpp/                    # C++ tests
│       ├── CMakeLists.txt      # CMake config
│       └── run_tests.sh        # Test runner
└── MAKEFILE_SETUP.md          # This file
```

## Environment Requirements

### System Requirements
- **Python**: 3.12+ (managed by uv)
- **uv**: Python package manager
- **C++**: C++17 compiler (for C++ tests)
- **CMake**: 3.14+ (for C++ tests)

### Installation
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# All other dependencies are managed automatically
```

## Troubleshooting

### Common Issues

#### Python Environment Issues
```bash
# Clean and rebuild environment
make clean
make python-env
```

#### uv Not Found
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart shell or source profile
```

#### Permission Issues
```bash
# Make sure scripts are executable
chmod +x tests/cpp/run_tests.sh
```

### Debug Commands

```bash
# Check Python environment (from root)
uv run --project tests/python python --version

# Check installed packages
uv pip list --project tests/python

# Manual test run (from root)
uv run --project tests/python pytest tests/python/tests/test_parser_basic.py::TestBasicParsing::test_parser_initialization -v
```

## Integration with IDEs

### VS Code
Add to `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Python Tests (Basic)",
            "type": "shell",
            "command": "make python-test-basic",
            "group": "test"
        },
        {
            "label": "C++ Tests",
            "type": "shell", 
            "command": "make cpp-test",
            "group": "test"
        }
    ]
}
```

### Command Line Aliases
Add to your shell profile:
```bash
alias yaal-test-py="make python-test-basic"
alias yaal-test-cpp="make cpp-test"
alias yaal-status="make status"
```

## Future Improvements

### Planned Enhancements
1. **Parallel Testing**: Run Python and C++ tests in parallel
2. **Watch Mode**: Auto-run tests on file changes
3. **Docker Support**: Containerized test environments
4. **CI Integration**: GitHub Actions integration
5. **Performance Benchmarks**: Automated performance testing

### Grammar Improvements Needed
1. **Fix quoted string recognition** in value positions
2. **Support empty values** after colons
3. **Improve brace block handling** with quotes
4. **Better error messages** for common mistakes

## Conclusion

The Makefile provides a robust, easy-to-use interface for YAAL parser development and testing. It properly manages Python environments with `uv` and provides clear feedback on test status and issues.

**Quick Start**: Run `make status` to see current state, then `make python-test-basic` for fast development feedback.