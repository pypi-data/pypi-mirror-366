# Vector DB Query System Documentation

This directory contains the source files for the Vector DB Query System documentation.

## Building Documentation Locally

1. Install documentation dependencies:
   ```bash
   pip install -e ".[docs]"
   ```

2. Build the documentation:
   ```bash
   cd docs
   sphinx-build -b html . _build/html
   ```

3. View the documentation:
   ```bash
   open _build/html/index.html  # macOS
   xdg-open _build/html/index.html  # Linux
   start _build/html/index.html  # Windows
   ```

## Documentation Structure

- `index.rst` - Main documentation index
- `installation.rst` - Installation guide
- `getting-started.rst` - Quick start tutorial
- `user-guide/` - Detailed user documentation
- `api/` - API reference documentation
- `contributing.rst` - Contribution guidelines
- `changelog.rst` - Version history

## Contributing to Documentation

1. Write documentation in reStructuredText format (.rst)
2. Use Google-style docstrings in Python code
3. Add code examples where helpful
4. Test the documentation build before submitting

## ReadTheDocs Integration

This documentation is automatically built and hosted on ReadTheDocs when changes are pushed to the main branch.

Configuration file: `.readthedocs.yaml`