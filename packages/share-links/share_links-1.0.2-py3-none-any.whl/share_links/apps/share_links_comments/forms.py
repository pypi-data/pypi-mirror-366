from django_comments.forms import CommentForm
from simplemathcaptcha.fields import MathCaptchaField

from share_links.apps.share_links_comments.models import CommentwithCaptcha


class CommentwithCaptchaForm(CommentForm):
    captcha = MathCaptchaField()

    def get_comment_create_data(self, **kwargs):
        data = super().get_comment_create_data(**kwargs)
        return data

    def get_comment_model(self):
        if "captcha" in self.cleaned_data:
            del self.cleaned_data["captcha"]
        return CommentwithCaptcha
