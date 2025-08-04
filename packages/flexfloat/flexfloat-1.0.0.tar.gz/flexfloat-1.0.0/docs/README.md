# FlexFloat Documentation

This directory contains the Sphinx documentation for FlexFloat.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- FlexFloat package installed

### Setup

1. Install documentation dependencies:
   ```bash
   pip install -e ".[docs]"
   ```

2. Build the documentation:
   ```bash
   cd docs
   make html
   ```

3. View the documentation:
   ```bash
   # Open docs/build/html/index.html in your browser
   ```

## Building Documentation

### Basic Build
```bash
cd docs
make html          # Build HTML documentation
make clean         # Clean build directory
make linkcheck     # Check for broken links
```

### Advanced Options
```bash
make strict        # Build with warnings as errors
make livehtml      # Build with live reload (requires sphinx-autobuild)
```

## Customization

### Theme and Styling
- Theme: Sphinx RTD Theme
- Custom CSS: `source/_static/custom.css`

### Configuration
Main configuration is in `source/conf.py`:
- Project metadata
- Extensions
- Theme options
- Version information

### Adding Content

#### New Pages
1. Create `.rst` files in appropriate directories
2. Add to relevant `toctree` directives
3. Follow existing structure and style

#### API Documentation
API docs are automatically generated from docstrings using:
- `sphinx.ext.autodoc`
- `sphinx.ext.autosummary`
- `sphinx.ext.napoleon` (for Google/NumPy style docstrings)

#### Examples
Add examples in `source/examples/` directory with practical use cases.

### Manual Deployment
```bash
# Build documentation
make html

# Deploy to GitHub Pages (manual)
# Copy docs/build/html/* to gh-pages branch
```

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Sphinx RTD Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [Read the Docs](https://docs.readthedocs.io/)
