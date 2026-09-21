import os
import sys
from importlib import metadata

sys.path.insert(0, os.path.abspath(".."))

project = "pymbrola"
copyright = "2024, NeuroDevCo"
author = "Gonzalo García-Castro"
release = metadata.version("mbrola")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_parser",
    "atsphinx.audioplayer",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
autosummary_generate = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = [".rst", ".md"]

# HTML theme settings
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_logo = "_static/img/logo.png"
html_favicon = "_static/img/logo.png"
html_css_files = ["styles/style.css", "styles/fonts.css"]

html_theme_options = {
    "github_url": "https://github.com/NeuroDevCo/pymbrola",
    "navbar_align": "left",
    "show_nav_level": 2,
    "back_to_top_button": True,
}

# MyST Parser
myst_enable_extensions = ["dollarmath", "amsmath"]

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
    "html_search_language": "en",
}

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

pygments_style = "sphinx"

## Copy button
copybutton_prompt_text = ">>> "
copybutton_exclude = ".linenos, .gp"
