# -*- coding: utf-8 -*-

project = "Задержка API"
author = "Иван Большаков, Владислав Рождественский"
copyright = "2026, Иван Большаков, Владислав Рождественский"
language = "ru"
extensions = [
    "myst_parser",
    "sphinx.ext.mathjax",
    "sphinxcontrib.bibtex",
    "sphinx_design",
]
exclude_patterns = ["_build"]
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "dollarmath",
    "html_image",
]
myst_dmath_double_inline = True
myst_footnote_transition = False
bibtex_bibfiles = ["refs.bib"]
bibtex_reference_style = "author_year"
source_suffix = {".md": "markdown"}
html_theme = "furo"
html_static_path = ["_static"]
html_title = project
mathjax3_config = {
    "tex": {
        "tags": "ams",
        "inlineMath": [["$", "$"], ["\\(", "\\)"]],
        "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
    }
}
