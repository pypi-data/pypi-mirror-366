from django.conf import settings

truthy_values = ("true", "True", "1", "yes", "Yes", "y", "Y")

if hasattr(settings, "SHARE_LINKS_USE_WEASYPRINT"):
    USE_WEASYPRINT = (
        True if settings.SHARE_LINKS_USE_WEASYPRINT in truthy_values else False
    )
else:
    USE_WEASYPRINT = False

if hasattr(settings, "SHARE_LINKS_SHOW_WEBARCHIVE_LINK"):
    SHOW_WEBARCHIVE_LINK = (
        True if settings.SHARE_LINKS_SHOW_WEBARCHIVE_LINK in truthy_values else False
    )
else:
    SHOW_WEBARCHIVE_LINK = True

if hasattr(settings, "SHARE_LINKS_DISPLAY_FAVICONS"):
    DISPLAY_FAVICONS = (
        True if settings.SHARE_LINKS_DISPLAY_FAVICONS in truthy_values else False
    )
else:
    DISPLAY_FAVICONS = False

if hasattr(settings, "SHARE_LINKS_FAVICON_SERVICE_URL"):
    FAVICON_SERVICE_URL = settings.SHARE_LINKS_FAVICON_SERVICE_URL
else:
    FAVICON_SERVICE_URL = "https://icons.duckduckgo.com/ip3/"

if hasattr(settings, "SHARE_LINKS_FAVICON_EXTENSION"):
    FAVICON_EXTENSION = settings.SHARE_LINKS_FAVICON_EXTENSION
else:
    FAVICON_EXTENSION = ".ico"

if hasattr(settings, "SHARE_LINKS_SEARCH_MIN_LENGTH"):
    SEARCH_MIN_LENGTH = int(settings.SHARE_LINKS_SEARCH_MIN_LENGTH)
else:
    SEARCH_MIN_LENGTH = 5

if hasattr(settings, "SHARE_LINKS_PAGINATION_SIZE"):
    PAGINATION_SIZE = int(settings.SHARE_LINKS_PAGINATION_SIZE)
else:
    PAGINATION_SIZE = 10
