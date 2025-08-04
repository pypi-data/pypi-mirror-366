# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'sphinxcontrib-giscus'
copyright = '2024, un4gt'
author = 'un4gt'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinxcontrib_giscus']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

data_repo = 'un4gt/un4gt.github.io'
data_repo_id = 'R_kgDOLqJB9g'
data_category = 'Announcements'
data_category_id = 'DIC_kwDOLqJB9s4CjTar'

html_favicon = "sphinxcontrib-giscus.ico"