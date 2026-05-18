project = "pymbrola"
copyright = "2024, NeuroDevCo"
author = "Gonzalo García-Castro"
release = "0.3.23"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_gallery.load_gallery",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML theme settings
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

html_theme_options = {
    "github_url": "https://github.com/NeuroDevCo/pymbrola",
    "search_analytics_id": "",
    "analytics_id": "",
    "navbar_align": "left",
    "footer_items": ["copyright", "sphinx-version"],
}

# Sphinx Gallery
sphinx_gallery_conf = {
    "examples_dirs": "examples",
    "gallery_dirs": "auto_examples",
    "mod_example_dir": "modules/generated",
    "doc_module": ("pymbrola",),
    "reference_url": {"pymbrola": None},
    "capture_repr": ("_repr_html_", "__repr__"),
    "ignore_repr_types": r"matplotlib.animation.FuncAnimation",
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
}

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}
