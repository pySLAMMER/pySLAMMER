# Configuration file for the Sphinx documentation builder.

# import subprocess
import os

# -- Project information -----------------------------------------------------

project = 'pySLAMMER'
author = 'Lorne Arnold, Donald Garcia-Rivas'
copyright = "2024"
release = '0.1.19'

master_doc = "index"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_nb",
    "sphinx_design",
    "autodoc2",
    # 'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

autodoc2_packages = [
    "../pyslammer",
]

# Check for these or similar settings in conf.py
# autodoc2_output_dir = "apidocs"
# autodoc2_index_template = "{objects}"  # This might be creating an index.md
# autodoc2_render_plugin = "myst"  # For .md output


myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "dollarmath",
    "amsmath",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "colon_fence"
    # "smartquotes",
    # "replacements",
    # "linkify",
    # "strikethrough",
    # "substitution",
    # "tasklist",
]

myst_url_schemes = ("http", "https", "mailto")



nb_execution_mode = "off"

templates_path = ['_templates']
exclude_patterns = []

# Shorten the path for doctrees
doctreedir = os.path.join(os.path.abspath('.'), '_doctrees')

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_book_theme"
html_logo = "_static/pySLAMMER_logo_wide.svg"
html_favicon = "_static/pySLAMMER_logo_square.svg"
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "home_page_in_toc": True,
    "show_navbar_depth": 1,
    "secondary_sidebar_items": {
    "**": ["page-toc"],
    "index": [],
    },
    "logo": {
        "text": "pySLAMMER"
    },
    "repository_url": "https://github.com/lornearnold/pyslammer",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_edit_page_button": False,
    "use_issues_button": False,
    # "announcement": "<b>v3.0.0</b> is now out! See the Changelog for details",
}

html_static_path = ['_static']