"""
# @Project sphinxcontrib-giscus
# @File    _constant.py
# @Author  MT308
# @Date    2024/11/25 22:18
"""

GISCUS_SCRIPT = """
<div class="giscus-container" style="margin-top: 2em; padding: 1em; border-top: 1px solid #ddd;">
<script src="https://giscus.app/client.js"
        data-repo="{}"
        data-repo-id="{}"
        data-category="{}"
        data-category-id="{}"
        data-mapping="{}"
        data-strict="{}"
        data-reactions-enabled="{}"
        data-emit-metadata="{}"
        data-input-position="{}"
        data-theme="{}"
        data-lang="{}"
        data-loading="{}"
        crossorigin="{}"
        async>
</script>
</div>
"""