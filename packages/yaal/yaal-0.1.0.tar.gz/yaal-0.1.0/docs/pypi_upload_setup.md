# PyPI Upload Setup for YAAL

This document explains how to set up PyPI credentials for uploading the YAAL package.

## The Problem

When running `make python-upload`, you might see:
```
⚠️  Make sure you have set up your PyPI credentials!
📤 Uploading to PyPI...
uv publish
Publishing 2 files https://upload.pypi.org/legacy/
Enter username ('__token__' if using a token):
```

This happens because `uv publish` doesn't automatically find credentials that work with other tools like `twine` or `pip`.

## Solutions

### Solution 1: Environment Variable (Recommended)

Set the `UV_PUBLISH_TOKEN` environment variable with your PyPI API token:

```bash
# Set for current session
export UV_PUBLISH_TOKEN="pypi-your-api-token-here"

# Then upload
make python-upload
```

**To make it permanent**, add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export UV_PUBLISH_TOKEN="pypi-your-api-token-here"
```

### Solution 2: Alternative Environment Variable

If you already have a `PYPI_TOKEN` variable set (from other projects), the Makefile will automatically use it:

```bash
export PYPI_TOKEN="pypi-your-api-token-here"
make python-upload
```

### Solution 3: One-time Token Upload

Use the token parameter for a single upload:

```bash
make python-upload-with-token TOKEN="pypi-your-api-token-here"
```

### Solution 4: Interactive Upload

If you prefer to enter credentials manually each time:

```bash
# Build the package first
make python-build

# Then upload manually with uv
uv publish
# Enter '__token__' as username and your token as password
```

## Getting a PyPI API Token

1. **Create PyPI Account**: Go to [pypi.org](https://pypi.org) and create an account
2. **Generate API Token**: 
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Choose scope (project-specific or account-wide)
   - Copy the generated token (starts with `pypi-`)

3. **Test Upload to Test PyPI** (recommended for first time):
   ```bash
   # Upload to test PyPI first
   UV_PUBLISH_URL="https://test.pypi.org/legacy/" \
   UV_PUBLISH_TOKEN="pypi-your-test-token" \
   uv publish
   ```

## Makefile Targets

### `make python-upload`
- **Requires**: `UV_PUBLISH_TOKEN` or `PYPI_TOKEN` environment variable
- **Does**: Builds package and uploads to PyPI
- **Fails gracefully**: Shows helpful error if no token found

### `make python-upload-with-token TOKEN=xyz`
- **Requires**: Token provided as parameter
- **Does**: Builds package and uploads with provided token
- **Usage**: `make python-upload-with-token TOKEN="pypi-your-token"`

### `make python-build`
- **Does**: Only builds the package (no upload)
- **Output**: Creates `dist/yaal-0.1.0.tar.gz` and `dist/yaal-0.1.0-py3-none-any.whl`

## Security Best Practices

### 1. Use Project-Specific Tokens
Create a token specifically for the YAAL project rather than using account-wide tokens.

### 2. Environment Variables
Store tokens in environment variables, not in code or configuration files.

### 3. Test First
Always test uploads with Test PyPI before uploading to production PyPI.

### 4. Rotate Tokens
Regularly rotate your API tokens for security.

## Troubleshooting

### "No module named 'twine'"
This error means you're trying to use `twine` instead of `uv publish`. The YAAL project uses `uv` for publishing.

### "Invalid credentials"
- Check that your token starts with `pypi-`
- Verify the token hasn't expired
- Make sure you're using the correct token for the target repository

### "Package already exists"
- You're trying to upload a version that already exists
- Increment the version in `pyproject.toml`
- Or use Test PyPI for testing

### "Permission denied"
- Your token doesn't have permission for this package
- Use an account-wide token or get added as a maintainer

## Example Workflow

```bash
# 1. Set up credentials (one time)
export UV_PUBLISH_TOKEN="pypi-your-token-here"

# 2. Make changes to the code
# 3. Update version in pyproject.toml if needed

# 4. Test the package
make python-test

# 5. Build and upload
make python-upload

# Or build and test locally first
make python-build
# Test the built package
pip install dist/yaal-0.1.0-py3-none-any.whl
yaal --version
# Then upload
make python-upload
```

## Integration with Other Tools

If you're using other Python packaging tools, you can share credentials:

### From twine/pip configuration
If you have `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-your-token-here
```

Extract the token:
```bash
export UV_PUBLISH_TOKEN=$(grep password ~/.pypirc | cut -d' ' -f3)
```

### From keyring
If you use keyring for credential storage:
```bash
export UV_PUBLISH_TOKEN=$(keyring get pypi __token__)
```

## Summary

The recommended approach is:
1. **Get a PyPI API token** from pypi.org
2. **Set environment variable**: `export UV_PUBLISH_TOKEN="pypi-your-token"`
3. **Upload**: `make python-upload`

This provides a secure, automated way to upload packages without manual credential entry.