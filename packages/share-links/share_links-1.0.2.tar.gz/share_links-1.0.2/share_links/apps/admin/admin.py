from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class ShareLinksAdmin(admin.AdminSite):
    site_header = _("Share links admin")
