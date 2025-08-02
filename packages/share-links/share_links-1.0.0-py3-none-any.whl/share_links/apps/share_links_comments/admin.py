from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .models import CommentwithCaptcha


@admin.register(CommentwithCaptcha)
class CommentwithCaptchaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "submit_date",
        "user_name",
        "user_email",
        "user_url",
        "comment",
        "link_url",
        "is_public",
        "is_removed",
        "comment_url",
    ]
    list_display_links = ["submit_date"]
    date_hierarchy = "submit_date"
    list_editable = ["is_public", "is_removed"]
    readonly_fields = [
        "user_name",
        "user",
        "user_email",
        "submit_date",
        "ip_address",
        "link_url",
        "link_comments",
        "id",
        "site",
    ]
    list_select_related = True

    fieldsets = (
        (None, {"fields": ("id", "is_public", "is_removed", "comment", "user_url")}),
        (
            _("User infos"),
            {
                "fields": ("user_name", "user_email", "ip_address"),
            },
        ),
        (
            _("Link infos"),
            {
                "fields": ("link_url", "link_comments"),
            },
        ),
    )

    def link_url(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse_lazy("link", None, (obj.object_pk,)),
            self.link_title(obj),
        )

    link_url.short_description = _("Link url")

    def link_comments(self, obj):
        return CommentwithCaptcha.objects.filter(object_pk=obj.object_pk).count()

    link_comments.short_description = _("Nb of link comments")

    def comment_url(self, obj):
        return format_html(
            '<a href="{}#c{}">{}</a>',
            reverse_lazy("link", None, (obj.object_pk,)),
            obj.pk,
            _("View"),
        )

    comment_url.short_description = _("Comment URL")

    def link_title(self, obj):
        try:
            if obj.content_object.title:  # if title exist (try/except) and is not None
                return obj.content_object.title
        except ObjectDoesNotExist:
            ...
        return obj.content_object.link

    def comment(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
