# Publishing to PyPI

This guide covers how to publish the Vector DB Query package to PyPI and Test PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts at:
   - Test PyPI: https://test.pypi.org/account/register/
   - PyPI: https://pypi.org/account/register/

2. **API Tokens**: Generate API tokens for both accounts:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/

3. **Install Tools**:
   ```bash
   pip install --upgrade twine build
   ```

## Configuration

1. Create `~/.pypirc` file with your API tokens:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   repository = https://upload.pypi.org/legacy/
   username = __token__
   password = pypi-AgEIcHlwaS5vcmc...  # Your PyPI token

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-AgENdGVzdC5weXBpLm9yZw...  # Your Test PyPI token
   ```

2. Set file permissions:
   ```bash
   chmod 600 ~/.pypirc
   ```

## Building the Package

1. Clean previous builds:
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   ```

2. Build the package:
   ```bash
   python -m build
   ```

3. Check the package:
   ```bash
   twine check dist/*
   ```

## Publishing to Test PyPI

1. Upload to Test PyPI:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. Test installation from Test PyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ vector-db-query
   ```

## Publishing to PyPI

Once tested, publish to the main PyPI:

```bash
twine upload dist/*
```

## Version Management

Before each release:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

## Troubleshooting

### Common Issues

1. **"Package already exists"**: Increment the version number in `pyproject.toml`

2. **Authentication failed**: Ensure your API token starts with `pypi-`

3. **Invalid package**: Run `twine check dist/*` to identify issues

### Manual Upload (without .pypirc)

For Test PyPI:
```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

For PyPI:
```bash
twine upload dist/*
```

You'll be prompted for username (use `__token__`) and password (your API token).

## Security Notes

- Never commit `.pypirc` to version control
- Use API tokens instead of passwords
- Consider using environment variables for CI/CD:
  ```bash
  export TWINE_USERNAME=__token__
  export TWINE_PASSWORD=your-api-token
  ```