# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'RAMAC'
author = 'Subrata Mukherjee, Qian Cao'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser","sphinx.ext.autodoc", "sphinx.ext.coverage", "sphinx.ext.napoleon","nbsphinx", "sphinx.ext.autosummary"]

#templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
nbsphinx_allow_errors = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_logo = "ramac_logo.png"
html_static_path = ['_static']
