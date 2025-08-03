def get_model():
    from share_links.apps.share_links_comments.models import (  # noqa E402
        CommentwithCaptcha,
    )

    return CommentwithCaptcha


def get_form():
    from share_links.apps.share_links_comments.forms import (  # noqa E402
        CommentwithCaptchaForm,
    )

    return CommentwithCaptchaForm


from .apps import ShareLinksCommentsConfig  # noqa E402

default_app_config = ShareLinksCommentsConfig
