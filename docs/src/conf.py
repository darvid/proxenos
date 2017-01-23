# -*- coding: utf-8 -*-
import pkg_resources


author = u'David Gidwani'
copyright = u'2017, David Gidwani'
exclude_patterns = []
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon',
    'sphinxcontrib.bibtex',
]
html_static_path = []
html_theme = 'material_design'
html_theme_options = {'pygments_theme': 'lovelace'}
intersphinx_mapping = {
    'https://docs.python.org/': None,
}
master_doc = 'index'
project = u'proxenos'
pygments_style = 'sphinx'
release = version = pkg_resources.get_distribution(
    'proxenos').version
source_suffix = '.rst'
templates_path = ['_templates']
todo_include_todos = True
