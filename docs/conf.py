import os
import sys
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from version import get_version_string, get_version_tuple

#!/usr/bin/env python3
"""
Sphinx Configuration for Documentation
======================================

This configuration file controls the Sphinx documentation builder.
It follows Eidosian principles: structured, precise, and adaptive to context.
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Path Configuration - Directory Structure Management
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Determine the absolute path to the documentation directory
docs_path = Path(__file__).parent.absolute()
# Determine the absolute path to the project root directory
root_path = docs_path.parent

# Add project root to Python path for proper import resolution
sys.path.insert(0, str(root_path))
# Also add the docs directory itself for any local extensions
sys.path.insert(0, str(docs_path))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Project Information - Core Identity
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
project = "Eidosian Project"
copyright = f"2023-{datetime.datetime.now().year}, Eidosian"
author = "Eidosian"

# Version handling - gracefully falls back to defaults if version module not found
try:
    # Try multiple common version locations
    if (root_path / "version.py").exists():
        sys.path.insert(0, str(root_path))
        version = get_version_string()
        release = version
    elif (root_path / "src" / project.lower().replace(" ", "_") / "version.py").exists():
        version = get_version_string()
        release = version
    else:
        # Try to extract version from package metadata if installed
        try:
            import importlib.metadata
            version = importlib.metadata.version(project.lower().replace(" ", "_"))
            release = version
        except (ImportError, importlib.metadata.PackageNotFoundError):
            version = "0.1.0"
            release = version
except ImportError:
    version = "0.1.0"
    release = version

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# General Configuration - Core Behavior Settings
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
extensions = [
    # Core Sphinx extensions
    "sphinx.ext.autodoc",          # Automatic API documentation
    "sphinx.ext.viewcode",         # Add links to view source code
    "sphinx.ext.napoleon",         # Support for NumPy and Google style docstrings
    "sphinx.ext.autosummary",      # Generate summary tables for API
    "sphinx.ext.intersphinx",      # Link to other Sphinx documentation
    "sphinx.ext.coverage",         # Check documentation coverage
    "sphinx.ext.todo",             # Support for TODO items
    "sphinx.ext.ifconfig",         # Conditional content
    
    # External extensions
    "myst_parser",                 # Support for Markdown
    "sphinx_rtd_theme",            # ReadTheDocs theme
    "sphinx_copybutton",           # Add copy button to code blocks
    "sphinx_autodoc_typehints",    # Better type annotations display
]

# Look for autodoc_typing_extensions, gracefully degrade if not available
try:
    extensions.append("autodoc_typing_extensions")
except ImportError:
    pass

# Look for sphinxcontrib.mermaid, add if available
try:
    import sphinxcontrib.mermaid
    extensions.append("sphinxcontrib.mermaid")
except ImportError:
    pass

# MyST Parser configuration
myst_enable_extensions = [
    "amsmath",          # Advanced math support
    "colon_fence",      # Alternative to backticks for code blocks
    "deflist",          # Definition lists
    "dollarmath",       # Inline and block math with $
    "html_image",       # HTML image syntax
    "linkify",          # Auto-link bare URLs
    "replacements",     # Text replacements
    "smartquotes",      # Smart quotes
    "tasklist",         # GitHub-style task lists
]
myst_heading_anchors = 4  # Generate anchors for h1-h4 headings

# Napoleon settings (for Google-style docstrings)
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
napoleon_use_keyword = True
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}
autodoc_typehints = 'description'
autodoc_typehints_format = 'short'
autodoc_inherit_docstrings = True
autodoc_typehints_description_target = 'documented'

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# Template paths and patterns
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']

# Source file configurations
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
master_doc = 'index'

# Date formatting
today_fmt = '%Y-%m-%d'

# Default syntax highlighting language
highlight_language = 'python3'
pygments_style = 'sphinx'
pygments_dark_style = 'monokai'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HTML Output Configuration - Web Presentation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['css/custom.css']
html_js_files = ['js/custom.js']

# Try to create custom CSS directory and file if it doesn't exist
try:
    static_dir = docs_path / '_static' / 'css'
    static_dir.mkdir(parents=True, exist_ok=True)
    custom_css = static_dir / 'custom.css'
    if not custom_css.exists():
        with open(custom_css, 'w') as f:
            f.write("""/* Custom CSS for documentation */
:root {
    --font-size-base: 16px;
    --line-height-base: 1.5;
}

.wy-nav-content {
    max-width: 900px;
}

.highlight {
    border-radius: 4px;
}
""")
except Exception:
    pass

# ReadTheDocs theme options
html_theme_options = {
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

html_title = f"{project} {version} Documentation"
html_short_title = project
html_favicon = '_static/favicon.ico' if Path(docs_path / '_static' / 'favicon.ico').exists() else None
html_logo = '_static/logo.png' if Path(docs_path / '_static' / 'logo.png').exists() else None

# HTML extra settings
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True
html_copy_source = True
html_use_index = True
html_split_index = False
html_baseurl = ''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LaTeX/PDF Output Configuration - Print Presentation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'figure_align': 'htbp',
    'preamble': r'''
        \usepackage{charter}
        \usepackage[defaultsans]{lato}
        \usepackage{inconsolata}
    ''',
}

latex_documents = [
    (master_doc, f'{project.lower().replace(" ", "_")}.tex', f'{project} Documentation',
     author, 'manual'),
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Additional Output Formats - EPUB, Man, Texinfo
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_show_urls = 'footnote'

man_pages = [
    (master_doc, project.lower().replace(" ", ""), f'{project} Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, project.lower().replace(" ", "_"), f'{project} Documentation',
     author, project, 'Project documentation.',
     'Miscellaneous'),
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Extension-specific Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TodoXT extension configuration (if included)
todo_include_todos = True
todo_emit_warnings = False
todo_link_only = False

# copybutton configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# Advanced autodoc settings for better API documentation
add_module_names = False  # Removes the module name prefix from object names
python_use_unqualified_type_names = True

# Conditional configurations
if 'sphinxcontrib.mermaid' in extensions:
    mermaid_version = "10.6.1"  # Use the latest stable version
    mermaid_init_js = "mermaid.initialize({startOnLoad:true, securityLevel:'loose'});"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# App Setup Hook - Runtime Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def setup(app):
    """Set up custom configurations for the Sphinx application."""
    # Add custom stylesheet if needed
    app.add_css_file('css/custom.css')
    
    # Register a custom directive, role, or domain if needed
    # app.add_directive('example', ExampleDirective)
    
    # Add custom event handlers if needed
    # app.connect('event-name', handler_function)
    
    # Indicate successful setup
    return {
        'version': version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
