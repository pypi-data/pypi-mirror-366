# Publishing Guide for MOA Python SDK

This guide explains how to build and publish the MOA Python SDK to PyPI.

## Prerequisites

1. **Development Environment Setup**
   ```bash
   git clone https://github.com/memof-ai/moa-sdk-python.git
   cd moa-sdk-python
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Required Accounts**
   - PyPI account: https://pypi.org/account/register/
   - TestPyPI account (for testing): https://test.pypi.org/account/register/

3. **Authentication Setup**
   - Generate API tokens from PyPI account settings
   - Configure tokens in your environment

## Pre-publishing Checklist

### 1. Code Quality
```bash
# Run all quality checks
black moa/ tests/ examples/
ruff check moa/ tests/ examples/
mypy moa/
pytest tests/ --cov=moa --cov-report=term-missing
```

### 2. Version Management
Update version in `moa/__init__.py`:
```python
__version__ = "0.1.1"  # Update version number
```

### 3. Documentation Updates
- Update `CHANGELOG.md` with new changes
- Ensure `README.md` is current
- Check that examples work with new version

### 4. Build Testing
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Check the built package
twine check dist/*
```

## Publishing Process

### Step 1: Test on TestPyPI (Recommended)

1. **Upload to TestPyPI**
   ```bash
   # Configure TestPyPI
   pip install twine

   # Upload to test repository
   twine upload --repository testpypi dist/*
   ```

2. **Test Installation from TestPyPI**
   ```bash
   # Create fresh environment
   python -m venv test_env
   source test_env/bin/activate
   
   # Install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ \
               --extra-index-url https://pypi.org/simple/ \
               memofai
   
   # Test the installation
   python -c "from memofai import MOAClient; print('Import successful!')"
   ```

### Step 2: Publish to PyPI

1. **Final Checks**
   ```bash
   # Ensure working directory is clean
   git status
   
   # Tag the release
   git tag v0.1.1
   git push origin v0.1.1
   ```

2. **Upload to PyPI**
   ```bash
   # Upload to production PyPI
   twine upload dist/*
   ```

3. **Verify Publication**
   ```bash
   # Install from PyPI
   pip install memofai
   
   # Test installation
   python -c "from memofai import MOAClient; print('PyPI installation successful!')"
   ```

## Automated Publishing with GitHub Actions

The repository includes a CI/CD pipeline that automatically publishes to PyPI when a release is created.

### Setup GitHub Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token

### Create a Release

1. Go to GitHub repository → Releases → Create a new release
2. Choose a tag (e.g., `v0.1.1`)
3. Fill in release title and description
4. Publish the release

The GitHub Action will automatically:
- Run tests on multiple Python versions
- Build the package
- Publish to PyPI if tests pass

## Manual Publishing Configuration

### Configure PyPI Credentials

1. **Using API Tokens (Recommended)**
   ```bash
   # Create ~/.pypirc file
   cat > ~/.pypirc << EOF
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-your-test-token-here
   EOF
   
   chmod 600 ~/.pypirc
   ```

2. **Using Environment Variables**
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-api-token-here
   ```

## Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check for missing dependencies
   pip install build twine
   
   # Clean and rebuild
   rm -rf dist/ build/ *.egg-info/
   python -m build
   ```

2. **Upload Errors**
   ```bash
   # Check package validity
   twine check dist/*
   
   # Verify authentication
   twine check --repository testpypi dist/*
   ```

3. **Version Conflicts**
   - Ensure version in `__init__.py` is unique
   - Check PyPI for existing versions
   - Use semantic versioning (major.minor.patch)

### Testing Installation

```bash
# Test in isolated environment
python -m venv fresh_test
source fresh_test/bin/activate
pip install memofai

# Run basic functionality test
python -c "
from memofai import MOAClient, Environment
print('✓ Import successful')
print('✓ Environment enum:', list(Environment))
client = MOAClient(api_key='test')
print('✓ Client creation successful')
print('✓ Client environment:', client.environment)
"
```

## Release Workflow

1. **Development Phase**
   - Work on feature branches
   - Merge to `develop` branch
   - Test thoroughly

2. **Release Preparation**
   - Merge `develop` to `main`
   - Update version number
   - Update changelog
   - Create comprehensive tests

3. **Release**
   - Tag the release
   - Create GitHub release
   - Automatic publishing via GitHub Actions
   - Manual verification

4. **Post-Release**
   - Update documentation
   - Announce on relevant channels
   - Monitor for issues

## Version Numbering

Follow semantic versioning (SemVer):
- **MAJOR** version: incompatible API changes
- **MINOR** version: functionality added (backward compatible)
- **PATCH** version: backward compatible bug fixes

Examples:
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features
- `1.0.0` - Stable API release
