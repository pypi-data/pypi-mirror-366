# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import logging
import os
import sys
from pathlib import Path

import flexfloat

# -- Path setup --------------------------------------------------------------

# Add the project root directory to the Python path so we can import the package
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def setup(app):
    """Setup function to configure Sphinx app."""

    # Create a custom logging filter
    class DuplicateObjectFilter(logging.Filter):
        def filter(self, record):
            # Filter out duplicate object description warnings
            return not (
                "duplicate object description" in record.getMessage()
                and any(
                    prop in record.getMessage()
                    for prop in ["sign", "exponent", "fraction"]
                )
            )

    # Apply the filter to the sphinx logger
    sphinx_logger = logging.getLogger("sphinx")
    sphinx_logger.addFilter(DuplicateObjectFilter())

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


# -- Project information -----------------------------------------------------

project = "FlexFloat"
copyright = "2025, Ferran Sanchez Llado"
author = "Ferran Sanchez Llado"

# The full version, including alpha/beta/rc tags
release = flexfloat.__version__
version = ".".join(release.split(".")[:2])  # Short version (e.g., "0.3")

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",  # Automatic documentation from docstrings
    "sphinx.ext.autosummary",  # Generate autodoc summaries
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "sphinx.ext.intersphinx",  # Link to other project's documentation
    "sphinx.ext.mathjax",  # Render math via JavaScript
    "sphinx.ext.githubpages",  # Publish HTML docs in GitHub pages
    "sphinx_rtd_theme",  # Read the Docs theme
    "sphinx_copybutton",  # Add copy button to code blocks
    "myst_parser",  # Markdown support
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# Suppress specific warnings
suppress_warnings = [
    "autodoc",  # Suppress all autodoc warnings including duplicate object warnings
    "app.add_node",  # Suppress add_node warnings
    "app.add_directive",  # Suppress add_directive warnings
    "ref.python",  # Suppress Python reference warnings
]

# The master toctree document.
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
html_theme_options = {
    "analytics_id": "",
    "analytics_anonymize_ip": False,
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980b9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom CSS files
html_css_files = [
    "custom.css",
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Extension configuration -------------------------------------------------

# napoleon configuration
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# autodoc configuration
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Enable type hint cross-referencing
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_type_aliases = {
    "BitArray": "flexfloat.BitArray",
}

# autosummary configuration
autosummary_generate = True
autosummary_imported_members = True

# intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# copybutton configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# -- HTML context configuration ---------------------------------------------

# Custom HTML context
html_context = {
    "READTHEDOCS": os.environ.get("READTHEDOCS", False),
    "github_user": "ferranSanchezLlado",
    "github_repo": "flexfloat-py",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}

# HTML title
html_title = f"{project} v{release}"

# Favicon (uncomment when you have a favicon.ico file)
# html_favicon = '_static/favicon.ico'

# Logo (uncomment when you have a logo.png file)
# html_logo = '_static/logo.png'

# Show source links
html_show_sourcelink = True

# Add edit on GitHub links
html_context.update(
    {
        "display_github": True,
        "github_user": "ferranSanchezLlado",
        "github_repo": "flexfloat-py",
        "github_version": "main",
        "conf_py_path": "/docs/source/",
    }
)
