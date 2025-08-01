# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

# Create documentation for the source code in the repo
# (instead of the installed code)
sys.path.insert(0, os.path.abspath('..'))

from linuxnet.iptables.metadata import _author_ as author
from linuxnet.iptables.metadata import _version_ as version
from linuxnet.iptables.metadata import _package_


# -- Project information -----------------------------------------------------

project = _package_.replace('.', '-')
copyright = '2022, 2023, Panagiotis Tsirigotis'

# The short X.Y version
# version = '2.1.12'

# The full version, including alpha/beta/rc tags
release = version

# -- General configuration ---------------------------------------------------

# Class documentation should come from the class docstring and
# the __init__ method docstring (the latter should describe
# __init__'s parameters)
autoclass_content = "both"

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for MANPAGE output -------------------------------------------------

man_pages = [
                ('iptables_api', 'linuxnet.iptables', 'iptables(8) programmatic access', author, 3),
                ]

man_make_section_directory = True
