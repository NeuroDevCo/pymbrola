# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "pymbrola"
copyright = "2026, Gonzalo García-Castro"
author = "Gonzalo García-Castro"
release = "v0.3.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "myst_parser",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",  # For Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # Optional: to include links to source code
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}


templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

Path("_static").mkdir(exist_ok=True)
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/NeuroDevCo/pymbrola",
            "icon": "fa-brands fa-github",
        },
    ],
    "navbar_align": "content",
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink", "donate"],
    "use_edit_page_button": True,
}

html_context = {
    "github_user": "NeuroDevCo",
    "github_repo": "pymbrola",
    "github_version": "main",
    "doc_path": "doc/source/",
    "default_mode": "light",
}
