#!/usr/bin/env python3
"""
Sphinx Configuration for Documentation
======================================

Welcome to the Eidosian configuration—where structure meets wit and digital brilliance.
This file controls our Sphinx documentation build, engineered to be as robust and universal
as the Eidosian spirit itself. Prepare to witness precision, creativity, and a hint of humour!
"""

import os
import sys
import datetime
from pathlib import Path
from typing import Any

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Path Configuration - Crafting our digital landscape
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Determine the absolute path to this documentation directory (our creative studio)
docs_path = Path(__file__).parent.absolute()
# Determine the project root (the base of our magnum opus)
root_path = docs_path.parent

# Enrich the Python path with our project and docs directories for flawless imports.
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(docs_path))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Project Information - The Heart of Eidosian Brilliance
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
project = "Doc Forge Project"
copyright = f"2025-{datetime.datetime.now().year}, MIT License"
# The copyright holder, a digital guardian of our creation.
author = "Lloyd Handyside"

# Version handling - Because every masterpiece deserves its signature.
try:
    # Attempt to import version functions if available
    from version import get_version_string, get_version_tuple
    if (root_path / "version.py").exists():
        sys.path.insert(0, str(root_path))
        version = get_version_string()
        release = version
    elif (root_path / "src" / project.lower().replace(" ", "_") / "version.py").exists():
        version = get_version_string()
        release = version
    else:
        # Fallback to package metadata, or default to a humble version number.
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# General Configuration - Our Toolkit of Extensions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Core Sphinx extensions are our stalwart artisans in this project.
extensions = [
    "sphinx.ext.autodoc",          # Automatic API documentation
    "sphinx.ext.viewcode",         # Source code viewer
    "sphinx.ext.napoleon",         # Google and NumPy style docstrings
]

# Conditionally enable additional extensions, only if they're installed.
for ext in [
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.todo",
    "sphinx.ext.ifconfig",
]:
    try:
        __import__(ext)
        extensions.append(ext)
    except ImportError:
        pass

# External extensions—if they exist, they add extra pizzazz.
for ext in [
    "myst_parser",
    "sphinx_rtd_theme",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.mermaid",
]:
    try:
        __import__(ext.split('.')[0])
        extensions.append(ext)
    except ImportError:
        pass

# MyST Parser configuration (if loaded) adds markdown magic.
if "myst_parser" in extensions:
    myst_enable_extensions = [
        "amsmath",          # Advanced math support
        "colon_fence",      # Alternative for code blocks
        "deflist",          # Definition lists
        "dollarmath",       # Inline/block math with $
        "html_image",       # HTML image syntax
        "linkify",          # Auto-link bare URLs
        "replacements",     # Text replacements
        "smartquotes",      # Intelligent quotes
        "tasklist",         # GitHub-style task lists
    ]
    myst_heading_anchors = 4  # Generate anchors for headings h1-h4

# Napoleon configuration: Embrace the beauty of structured docstrings.
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

# Autodoc settings - We like our API docs as clear as crystal.
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

# Intersphinx configuration (if enabled) to connect with the broader documentation cosmos.
if "sphinx.ext.intersphinx" in extensions:
    intersphinx_mapping = {
        'python': ('https://docs.python.org/3', None),
        'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    }

# Template paths and file exclusion patterns.
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']

# Source file configuration. By default, reStructuredText rules our world.
source_suffix = {'.rst': 'restructuredtext'}
if 'myst_parser' in extensions:
    source_suffix['.md'] = 'markdown'
master_doc = 'index'

# Date formatting for the chronicles of documentation.
today_fmt = '%Y-%m-%d'

# Syntax highlighting and Pygments settings.
highlight_language = 'python3'
pygments_style = 'sphinx'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HTML Output Configuration - Where Beauty Meets Functionality
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Choose the ReadTheDocs theme if available; otherwise, fall back to alabaster.
html_theme = 'sphinx_rtd_theme' if 'sphinx_rtd_theme' in extensions else 'alabaster'
html_static_path = ['_static']

# Ensure the _static directory exists, our canvas for custom art.
try:
    static_dir = docs_path / '_static'
    static_dir.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Set up custom CSS and JS only if their directories exist (or can be created).
html_css_files = ['css/custom.css'] if (docs_path / '_static' / 'css').mkdir(parents=True, exist_ok=True) or (docs_path / '_static' / 'css').exists() else []
html_js_files = ['js/custom.js'] if (docs_path / '_static' / 'js').mkdir(parents=True, exist_ok=True) or (docs_path / '_static' / 'js').exists() else []

# Create a custom CSS file if it does not yet exist—because style matters.
try:
    css_dir = docs_path / '_static' / 'css'
    css_dir.mkdir(parents=True, exist_ok=True)
    custom_css = css_dir / 'custom.css'
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

# If using the RTD theme, define its delightful options.
if html_theme == 'sphinx_rtd_theme':
    html_theme_options = {
        'prev_next_buttons_location': 'bottom',
        'style_external_links': True,
        'style_nav_header_background': '#2980B9',
        'collapse_navigation': False,
        'sticky_navigation': True,
        'navigation_depth': 4,
        'includehidden': True,
        'titles_only': False,
    }
    # Remove 'display_version' as it's unsupported

html_title = f"{project} {version} Documentation"
html_short_title = project
html_favicon = '_static/favicon.ico' if (docs_path / '_static' / 'favicon.ico').exists() else None
html_logo = '_static/logo.png' if (docs_path / '_static' / 'logo.png').exists() else None

# Additional HTML display settings to showcase our documentation in all its glory.
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True
html_copy_source = True
html_use_index = True
html_split_index = False
html_baseurl = ''

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LaTeX/PDF Output Configuration - For Printed Legacies
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Additional Output Formats - EPUB, Man, and Texinfo Chronicles
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_show_urls = 'footnote'

man_pages = [
    (master_doc, project.lower().replace(" ", ""), f'{project} Documentation', [author], 1)
]

texinfo_documents = [
    (master_doc, project.lower().replace(" ", "_"), f'{project} Documentation',
     author, project, 'Project documentation.', 'Miscellaneous'),
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Extension-specific and Miscellaneous Configurations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TodoXT configuration (if using TODOs in your docs)
todo_include_todos = True
todo_emit_warnings = False
todo_link_only = False

# Configure copybutton if available.
if 'sphinx_copybutton' in extensions:
    copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
    copybutton_prompt_is_regexp = True

# Advanced autodoc refinement—remove module prefixes for a cleaner look.
add_module_names = False
python_use_unqualified_type_names = True

# Mermaid configuration for flowcharts, if the extension is active.
if 'sphinxcontrib.mermaid' in extensions:
    mermaid_version = "10.6.1"
    mermaid_init_js = "mermaid.initialize({startOnLoad:true, securityLevel:'loose'});"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# App Setup Hook - Final Flourish and Runtime Customisation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def setup(app: Any) -> dict:
    """Set up custom configurations for the Sphinx application with Eidosian flair."""
    try:
        app.add_css_file('css/custom.css')
    except Exception:
        pass  # We are already Eidosian—if it fails, we simply carry on.
    # Additional directives or event handlers can be registered here.
    return {
        'version': version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Building Your Documentation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# To build your documentation in a truly Eidosian manner, use the following command:
#
#     python -m sphinx -b html docs/ $READTHEDOCS_OUTPUT/html/
#
# This ensures that Sphinx is invoked through Python's module interface—keeping our build
# process as modern and reliable as our digital dreams.
