"""
# @Project sphinxcontrib-giscus
# @File    _giscus.py
# @Author  MT308
# @Date    2024/11/25 22:22
"""
from sphinx.application import Sphinx
from sphinx.util import logging

from ._constant import GISCUS_SCRIPT

sphinxcontrib_giscus_logger = logging.getLogger('sphinxcontrib_giscus')

def add_giscus_script(app: Sphinx, pagename, templatename, context, doctree):
    if not app.config.enable_giscus:
        sphinxcontrib_giscus_logger.info('Giscus not enabled')
        return

    meta = context.get('meta', {})
    if not meta:
        return

    if 'giscus-on' in meta:
        sphinxcontrib_giscus_logger.info(f'Trying to add giscus script at {pagename}')
        if 'body' in context:
            context['body'] += GISCUS_SCRIPT.format(
                app.config.data_repo,
                app.config.data_repo_id,
                app.config.data_category,
                app.config.data_category_id,
                app.config.data_mapping,
                app.config.data_strict,
                app.config.data_reactions_enabled,
                app.config.data_emit_metadata,
                app.config.data_input_position,
                app.config.data_theme,
                app.config.data_lang,
                app.config.data_loading,
                app.config.crossorigin,
            )
