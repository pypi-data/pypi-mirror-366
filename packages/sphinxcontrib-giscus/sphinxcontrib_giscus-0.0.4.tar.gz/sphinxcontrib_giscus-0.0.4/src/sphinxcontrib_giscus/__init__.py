from sphinx.application import Sphinx

from ._config import config_values, check_config
from ._giscus import add_giscus_script

__version__ = '0.0.2'


def setup(app: Sphinx):
    # config for giscus
    for cfg in config_values:
        app.add_config_value(cfg['name'], cfg['default'], cfg['rebuild'])

    app.add_config_value('enable_giscus', True, 'html')

    # check config
    app.connect('builder-inited', check_config)
    app.connect('html-page-context', add_giscus_script)

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
        'version': __version__,
    }