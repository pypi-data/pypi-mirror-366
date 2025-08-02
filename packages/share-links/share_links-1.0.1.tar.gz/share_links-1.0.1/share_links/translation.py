from modeltranslation.translator import TranslationOptions, register

from .models import AboutContactPages, Link, Tag


@register(Link)
class LinkTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = (
        "tag",
        "description",
    )


@register(AboutContactPages)
class AboutContactPagesTranslationOptions(TranslationOptions):
    fields = (
        "page_title",
        "description",
    )
