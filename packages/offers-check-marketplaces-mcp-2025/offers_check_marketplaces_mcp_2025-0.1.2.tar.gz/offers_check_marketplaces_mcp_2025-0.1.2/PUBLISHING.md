# Publishing Guide for offers-check-marketplaces

This guide explains how to build and publish the `offers-check-marketplaces` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org/) and [Test PyPI](https://test.pypi.org/)
2. **API Tokens**: Generate API tokens for both PyPI and Test PyPI
3. **Python Environment**: Ensure you have Python 3.10+ installed

## Setup

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Configure PyPI Credentials

Create a `.pypirc` file in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Publishing Process

### Method 1: Using the Automated Script

```bash
python publish.py
```

This script will:

1. Check requirements
2. Clean previous builds
3. Build the package
4. Check the package
5. Offer options to upload to Test PyPI or PyPI

### Method 2: Manual Process

#### Step 1: Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info/
```

#### Step 2: Build the Package

```bash
python -m build
```

#### Step 3: Check the Package

```bash
python -m twine check dist/*
```

#### Step 4: Upload to Test PyPI (Recommended First)

```bash
python -m twine upload --repository testpypi dist/*
```

#### Step 5: Test Installation from Test PyPI

```bash
pip install -i https://test.pypi.org/simple/ offers-check-marketplaces
```

#### Step 6: Upload to PyPI (Production)

```bash
python -m twine upload dist/*
```

## Pre-Publication Checklist

- [ ] Update version number in `pyproject.toml`
- [ ] Update `README.md` with latest features
- [ ] Update `CHANGELOG.md` (if exists)
- [ ] Run all tests: `pytest`
- [ ] Test license integration: `python test_license_integration.py`
- [ ] Test MCP tools: `python test_mcp_license_tools.py`
- [ ] Verify package metadata in `pyproject.toml`
- [ ] Check that all required files are included in `MANIFEST.in`

## Package Structure

```
offers-check-marketplaces/
├── offers_check_marketplaces/          # Main package
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py                       # Main MCP server
│   ├── license_manager.py              # License management
│   ├── database_manager.py             # Database operations
│   ├── search_engine.py                # Search functionality
│   ├── data_processor.py               # Excel processing
│   ├── statistics.py                   # Analytics
│   ├── error_handling.py               # Error management
│   ├── marketplace_client.py           # Marketplace clients
│   ├── marketplace_config.py           # Marketplace configuration
│   └── models.py                       # Data models
├── pyproject.toml                      # Package configuration
├── README.md                           # Package documentation
├── LICENSE                             # License file
├── MANIFEST.in                         # Additional files to include
├── setup.py                            # Compatibility setup
└── publish.py                          # Publishing script
```

## Version Management

Update the version in `pyproject.toml`:

```toml
[project]
name = "offers-check-marketplaces"
version = "0.1.1"  # Update this
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

## Testing the Published Package

### From Test PyPI

```bash
# Install from Test PyPI
pip install -i https://test.pypi.org/simple/ offers-check-marketplaces

# Test basic functionality
offers-check-marketplaces --help

# Test with license key
LICENSE_KEY="your-key" offers-check-marketplaces
```

### From PyPI

```bash
# Install from PyPI
pip install offers-check-marketplaces

# Test functionality
offers-check-marketplaces --help
```

## Common Issues and Solutions

### Issue: Package Already Exists

**Error**: `File already exists`

**Solution**: Update the version number in `pyproject.toml` and rebuild.

### Issue: Missing Dependencies

**Error**: Import errors when installing

**Solution**: Check `dependencies` in `pyproject.toml` and ensure all required packages are listed.

### Issue: License Validation Fails

**Error**: License check fails after installation

**Solution**: Ensure the license server is accessible and the API endpoint is correct.

### Issue: MCP Tools Not Working

**Error**: MCP tools not recognized

**Solution**: Verify the entry point in `pyproject.toml`:

```toml
[project.scripts]
offers-check-marketplaces = "offers_check_marketplaces.__main__:main"
```

## Post-Publication

1. **Update Documentation**: Update GitHub repository with installation instructions
2. **Create Release**: Create a GitHub release with changelog
3. **Announce**: Announce the release in relevant communities
4. **Monitor**: Monitor for issues and user feedback

## Security Considerations

- Never commit API tokens to version control
- Use environment variables for sensitive configuration
- Regularly rotate API tokens
- Monitor package downloads for suspicious activity

## Support

For issues with publishing:

1. Check [PyPI Help](https://pypi.org/help/)
2. Review [Twine Documentation](https://twine.readthedocs.io/)
3. Check [Python Packaging Guide](https://packaging.python.org/)

---

Happy publishing! 🚀
