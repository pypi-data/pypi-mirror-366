# GitHub Release Guide

This guide covers how to create a GitHub release for Vector DB Query System.

## Prerequisites

1. **GitHub Account**: Ensure you have push access to the repository
2. **Git Tag**: Create and push the version tag
3. **Distribution Files**: Build the package files

## Step 1: Create and Push Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to GitHub
git push origin v1.0.0
```

## Step 2: Create Release on GitHub

### Using GitHub Web Interface

1. Go to your repository on GitHub
2. Click on "Releases" (right sidebar)
3. Click "Draft a new release"
4. Choose the tag: `v1.0.0`
5. Release title: `Vector DB Query System v1.0.0`
6. Copy contents from `RELEASE_NOTES.md` to description
7. Upload distribution files:
   - `dist/vector_db_query-1.0.0-py3-none-any.whl`
   - `dist/vector_db_query-1.0.0.tar.gz`
8. Check "This is a pre-release" if testing
9. Click "Publish release"

### Using GitHub CLI

```bash
# Install GitHub CLI
brew install gh  # macOS
# or see: https://cli.github.com/

# Authenticate
gh auth login

# Create release
gh release create v1.0.0 \
  --title "Vector DB Query System v1.0.0" \
  --notes-file RELEASE_NOTES.md \
  dist/*.whl dist/*.tar.gz
```

## Step 3: Verify Release

1. Check the releases page on GitHub
2. Verify assets are attached correctly
3. Test download links

## Release Checklist

- [ ] Version updated in `pyproject.toml`
- [ ] `CHANGELOG.md` updated
- [ ] Tests passing
- [ ] Package builds successfully
- [ ] Tag created and pushed
- [ ] Release notes prepared
- [ ] Distribution files uploaded
- [ ] Release published

## Automation with GitHub Actions

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: RELEASE_NOTES.md
          draft: false
          prerelease: false
      
      - name: Upload Release Assets
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./dist/
          asset_name: dist
          asset_content_type: application/zip
```

## Post-Release

After creating the release:

1. **Announce**: Share on social media, forums, etc.
2. **Monitor**: Watch for issues and feedback
3. **Document**: Update README with installation instructions
4. **PyPI**: Upload to PyPI if not automated