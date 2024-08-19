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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "Dexsnake"
copyright = "2024, Leevi Kerkelä"
author = "Leevi Kerkelä"

# The full version, including alpha/beta/rc tags
# release = "0.0.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "nbsphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = "_static/dexsnake_logo.png"

html_theme_options = {
    "sidebar_hide_name": True,
    "light_css_variables": {
        "font-stack": "Ubuntu",
        "font-stack--monospace": "Ubuntu Mono",
        "color-brand-primary": "#ea43ed",
        "color-brand-content": "#ea43ed",
    },
    "dark_css_variables": {
        "font-stack": "Ubuntu",
        "font-stack--monospace": "Ubuntu Mono",
        "color-brand-primary": "#ea43ed",
        "color-brand-content": "#ea43ed",
    },
}

autoclass_content = "both"

# use default style since the styles below didn't work on readthedocs
# pygments_style = "stata-light"
# pygments_dark_style = "stata-dark"

# Ensure that typehints are shown correctly for properties
autodoc_typehints = "description"
