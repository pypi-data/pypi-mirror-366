from html.parser import HTMLParser
from re import search
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from zlib import MAX_WBITS, decompress

from django.conf.global_settings import LANGUAGES as FULL_LANGUAGES_LIST
from django.contrib.sites.models import Site
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from share_links.__version__ import version


def iri2uri(iri):
    """Thx https://stackoverflow.com/a/42309027/6813732 !"""
    uri = ""
    if isinstance(iri, str):
        (scheme, netloc, path, query, fragment) = urlsplit(iri)
        scheme = quote(scheme)
        netloc = netloc.encode("idna").decode("utf-8")
        path = quote(path)
        query = quote(query)
        fragment = quote(fragment)
        uri = urlunsplit((scheme, netloc, path, query, fragment))
    return uri


def get_full_url(url):
    parsed_url = urlparse(url)
    new_url = parsed_url.scheme + "://" + parsed_url.netloc + quote(parsed_url.path)
    if parsed_url.query:
        new_url += "?" + parsed_url.query
    new_url = iri2uri(new_url)
    return new_url


def get_request(url):
    request = Request(url)
    request.add_header("Accept-Encoding", "gzip, deflate")
    request.add_header(
        "Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    )
    request.add_header(
        "User-agent",
        f"share-links v{version} (gitlab.com/sodimel/share-links) instance ({Site.objects.get_current().domain})",
    )
    return request


class TitleParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.match = False
        self.title = []

    def handle_starttag(self, tag, attributes):
        self.match = tag == "title"

    def handle_data(self, data):
        if self.match:
            self.title.append(data)
            self.match = False


def get_parsed_html(url, request):
    try:
        html = urlopen(request, timeout=10).read()
        if html[0:3] == b"\x1f\x8b\x08":  # why tf is this html content still gzipped?
            # TODO: check size of content, if too big, dont decompress (gzip bomb)
            html = decompress(html, 16 + MAX_WBITS)
        html = html.decode("utf-8")
    except UnicodeDecodeError:
        html = html.decode("iso-8859-1")
    except HTTPError as e:
        if e.code == 404:  # not found
            return (
                False,
                _(
                    "Got a HTTP status of 404, Not found. The page does not exist anymore."
                ),
            )
        if (
            e.code == 406
        ):  # not acceptable - should not happen anymore since we're using a header to say we accept html, but just in case
            return (
                False,
                _(
                    "Got a HTTP status of 406, Not Acceptable. It seems that this page does not really like scrapping, you're gonna take the data yourself."
                ),
            )
        if e.code == 410:  # gone
            return (
                False,
                _(
                    "Got a HTTP status of 410, Gone. The resource is likely not available anymore."
                ),
            )
        return (False, _(f"Unknown error, HTTP code {e.code}."))
    except URLError:
        return (False, _("Url is unreachable."))
    return (True, html)


def get_title(url):
    url = get_full_url(url)
    request = get_request(url)
    status, html = get_parsed_html(url, request)
    if status is False:
        return (status, html)

    parser = TitleParser()
    parser.feed(html)
    if len(parser.title):
        title = mark_safe(parser.title[0].strip())
    else:
        title = None

    if title:
        return (True, title)
    return (False, _("Got an empty title, you'll need to be creative!"))


def get_lang(url):
    url = get_full_url(url)
    request = get_request(url)
    status, html = get_parsed_html(url, request)
    if status is False:
        return (status, html)

    match = search(r"lang=['\"]?([a-z]+)[\"']?>?", html)
    if match:
        match = match.group(1)
        for language in FULL_LANGUAGES_LIST:
            if match == language[0]:
                return (True, match)
        return (
            False,
            _(
                "Lang attribute found does not match any of available value in LANGUAGE_CHOICES."
            ),
        )
    return (False, _("Cannot find a lang attribute."))
