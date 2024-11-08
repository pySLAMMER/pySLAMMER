# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'pyslammer'
author = 'Lorne Arnold, Donald Garcia-Rivas'
release = '0.1.19'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'jupyter_sphinx',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']
