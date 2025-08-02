from urllib.parse import urlparse

from django import template
from django.conf.global_settings import LANGUAGES as FULL_LANGUAGES_LIST
from django.utils.translation import gettext_lazy as _

from share_links.__version__ import version
from share_links.conf import DISPLAY_FAVICONS, FAVICON_EXTENSION, FAVICON_SERVICE_URL

register = template.Library()


@register.filter()
def get_domain_name(url):
    if not url.startswith("http"):
        url = "https://" + url
    return urlparse(url).netloc


@register.filter()
def get_translated_language(lang):
    try:
        lang = dict(FULL_LANGUAGES_LIST)[lang]
        return _(f"This page is in {lang}.")
    except:  # noqa:E722
        return _(f"This page is in {lang}.")


@register.filter()
def get_links_nb(tag):
    return tag.links.count()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    # thx https://stackoverflow.com/a/56824200/6813732 !
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()


@register.filter(is_safe=True)
def get_version(context, **kwargs):
    return f"{context}{version}"


@register.filter(is_safe=True)
def show_favicon(domain_name):
    if DISPLAY_FAVICONS:
        favicon_service_url = FAVICON_SERVICE_URL
        favicon_extension = FAVICON_EXTENSION
        favicon_alt_title_text = _("Favicon of") + " " + domain_name
        return f'<img src="{favicon_service_url}{get_domain_name(domain_name)}{favicon_extension}" title="{favicon_alt_title_text}" class="favicon" />'
    return ""
