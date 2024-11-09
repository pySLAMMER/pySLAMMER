# Configuration file for the Sphinx documentation builder.

import subprocess
import os

# -- Project information -----------------------------------------------------

project = 'pyslammer'
author = 'Lorne Arnold, Donald Garcia-Rivas'
release = '0.1.19'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# Shorten the path for doctrees
doctreedir = os.path.join(os.path.abspath('.'), '_doctrees')

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
