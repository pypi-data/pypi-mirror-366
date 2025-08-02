from django.contrib.admin.apps import AdminConfig


class ShareLinksAdminConfig(AdminConfig):
    default_site = "share_links.apps.admin.admin.ShareLinksAdmin"
