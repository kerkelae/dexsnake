project = "Dexsnake"
copyright = "2024, Leevi Kerkelä"
author = "Leevi Kerkelä"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "nbsphinx",
]
nbsphinx_execute = "never"

html_theme = "furo"

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

pygments_style = "stata-light"
pygments_dark_style = "stata-dark"

autodoc_typehints = "description"
