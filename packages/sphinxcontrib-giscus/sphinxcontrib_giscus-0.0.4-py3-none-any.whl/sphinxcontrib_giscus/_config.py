"""
# @Project sphinxcontrib_giscus
# @File    _config.py
# @Author  MT308
# @Date    2024/11/25 20:50
"""
from typing import TypedDict, List

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.errors import ConfigError


sphinxcontrib_giscus_logger = logging.getLogger('sphinxcontrib_giscus')


class Cfg(TypedDict):
    name: str
    default: str
    rebuild: str


config_values: List[Cfg] = [
    {
        'name': 'data_repo',
        'default': '',
        'rebuild': 'html',
    },
    {
        'name': 'data_repo_id',
        'default': '',
        'rebuild': 'html',
    },
    {
        'name': 'data_category',
        'default': '',
        'rebuild': 'html',
    },
    {
        'name': 'data_category_id',
        'default': '',
        'rebuild': 'html',
    },
    {
        'name': 'data_mapping',
        'default': 'pathname',
        'rebuild': 'html',
    },
    {
        'name': 'data_strict',
        'default': '0',
        'rebuild': 'html',
    },
    {
        'name': 'data_reactions_enabled',
        'default': '1',
        'rebuild': 'html',
    },
    {
        'name': 'data_emit_metadata',
        'default': '0',
        'rebuild': 'html',
    },
    {
        'name': 'data_input_position',
        'default': 'bottom',
        'rebuild': 'html',
    },
    {
        'name': 'data_theme',
        'default': 'preferred_color_scheme',
        'rebuild': 'html',
    },
    {
        'name': 'data_lang',
        'default': 'zh-CN',
        'rebuild': 'html',
    },
    {
        'name': 'data_loading',
        'default': 'lazy',
        'rebuild': 'html',
    },
    {
        'name': 'crossorigin',
        'default': 'anonymous',
        'rebuild': 'html',
    }
]

def check_config(app: Sphinx):
    # check that config must be set
    for c in config_values[:4]:
        try:
            attr_val = getattr(app.config, c['name'])
            if not attr_val:
                raise ConfigError(f'config value {c["name"]} is not valid.')
        except AttributeError:
            sphinxcontrib_giscus_logger.error(f'config value {c["name"]} must be set')