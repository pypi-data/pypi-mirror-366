from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_comments.abstracts import CommentAbstractModel
from django_comments.signals import comment_will_be_posted
from simplemathcaptcha.fields import MathCaptchaField


class CommentwithCaptcha(CommentAbstractModel):
    captcha = MathCaptchaField()

    class Meta:
        verbose_name = _("Moderate comments")
        verbose_name_plural = _("Moderate comments")


@receiver(comment_will_be_posted, sender=CommentwithCaptcha)
def handle_comments(sender, comment, request, **kwargs):
    comment.is_public = False
