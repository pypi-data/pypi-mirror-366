from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext as _
from parler.admin import TranslatableAdmin, TranslatableStackedInline

from .admin_utils import HasAtLeastOneTagFilter, OnlineOfflineFilter, RandomFilter
from .models import AboutContactPages, Category, Collection, CollectionLink, Link, Tag


@admin.register(AboutContactPages)
class AboutContactPagesAdmin(TranslatableAdmin):
    list_display = ("name",)

    def name(self, obj):
        if obj == AboutContactPages.objects.first():
            return _("About page")
        else:
            return _("Contact page")

    def message_user(self, *args):  # overridden method
        pass

    def save_delete_msg(self, request):
        messages.warning(
            request,
            _(
                "You can only create two \"AboutContactPages\" instances (first is About page, second is Contact page), and you can't delete any of them! If you know what you're doing, you can still add/delete objects using the model directly (not the admin like now)."
            ),
        )
        return False

    def delete_queryset(self, request, queryset):
        return self.save_delete_msg(request)

    def delete_model(self, request, client):
        return self.save_delete_msg(request)

    def save_model(self, request, obj, form, change):
        if AboutContactPages.objects.count() == 2 and not obj.id:
            return self.save_delete_msg(request)
        else:
            super(AboutContactPagesAdmin, self).save_model(request, obj, form, change)


@admin.register(Link)
class LinkAdmin(TranslatableAdmin):
    search_fields = ["id", "translations__title", "link"]

    list_select_related = True

    list_filter = (RandomFilter, OnlineOfflineFilter, HasAtLeastOneTagFilter)

    list_display = (
        "date_added",
        "highlight",
        "online",
        "link",
        "title_sortable",
        "view_link",
        "language",
        "added_by",
        "file_exist",
        "webarchive_url",
    )
    list_display_links = ("date_added",)

    list_editable = (
        "highlight",
        "online",
        "language",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "link",
                    ("online", "highlight"),
                    (
                        "title",
                        "language",
                    ),
                    "tags",
                    "description",
                )
            },
        ),
        (
            _("How to handle updates?"),
            {
                "fields": (
                    (
                        "allow_override_title",
                        "allow_override_language",
                    ),
                )
            },
        ),
        (
            _("Save file"),
            {
                "fields": (
                    (
                        "file",
                        "save_file",
                    ),
                )
            },
        ),
    )

    autocomplete_fields = [
        "tags",
    ]

    actions = ("add_tags",)

    class Media:
        js = ("share_links/fetch_title_of_url.js",)
        css = {"all": ("share_links/fetch_title_of_url.css",)}

    @admin.display(boolean=True)
    def file_exist(self, obj):
        return bool(obj.file)

    file_exist.short_description = _("File exist?")

    def title_sortable(self, obj):
        return obj.title

    title_sortable.short_description = _("Title")
    title_sortable.admin_order_field = "translations__title"

    def webarchive_url(self, obj):
        return format_html(
            '<a href="https://web.archive.org/save/{}" target="_blank">{}</a>',
            obj.link,
            _("Save this"),
        )

    webarchive_url.allow_tags = True
    webarchive_url.short_description = _("Web archive")

    def view_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse_lazy("link", None, (obj.id,)),
            _("View"),
        )

    @admin.action(description=_("Add tags to current selection"))
    def add_tags(self, request, queryset):
        links_selected = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(
            "add-tags/?ids=%s" % (",".join(str(pk) for pk in links_selected),)
        )

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.added_by = request.user
        super(LinkAdmin, self).save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        add_tags_url = [
            path("add-tags/", self.admin_site.admin_view(self.add_tags_view))
        ]
        return add_tags_url + urls

    def add_tags_view(self, request):
        links = Link.objects.filter(
            id__in=[int(id) for id in request.GET["ids"].split(",")]
        )
        if request.method == "POST":
            tags = Tag.objects.filter(
                id__in=[int(id) for id in request.POST.getlist("tags_select")]
            )
            for link in links:
                link.tags.add(*tags)
                link.save()

            self.message_user(
                request,
                _(
                    f"{len(links)} links where updated with the new tags {', '.join([str(tag) for tag in tags])}.",
                ),
                messages.SUCCESS,
            )
            return HttpResponseRedirect(
                reverse_lazy(
                    "admin:%s_%s_changelist"
                    % (self.model._meta.app_label, self.model._meta.model_name)
                )
            )
        else:
            tags = Tag.objects.all()

            class AddTagForm(forms.Form):
                tags_select = forms.ModelMultipleChoiceField(
                    widget=forms.CheckboxSelectMultiple, required=True, queryset=tags
                )

            form = AddTagForm()

            context = dict(
                self.admin_site.each_context(request), links=links, tags=tags, form=form
            )
            return TemplateResponse(request, "admin/add_tags.html", context)


@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    search_fields = ["translations__tag", "translations__slug"]

    autocomplete_fields = [
        "category",
    ]

    list_display = ("tag", "highlight", "link_nb", "slug")

    list_editable = ("highlight",)

    fieldsets = (
        (
            None,
            {
                "fields": ("tag", "slug", "category", "description", "highlight"),
            },
        ),
    )

    def link_nb(self, obj):
        return Link.objects.filter(tags=obj).count()

    link_nb.short_description = _("Link nb")


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    search_fields = ["label"]

    list_display = ("label", "tag_nb")

    def tag_nb(self, obj):
        return Tag.objects.filter(category=obj).count()

    tag_nb.short_description = _("Tag nb")


class CollectionLinkInline(TranslatableStackedInline, admin.StackedInline):
    model = CollectionLink
    autocomplete_fields = [
        "link",
    ]


@admin.register(Collection)
class CollectionAdmin(TranslatableAdmin):
    fields = [
        "name",
        "description",
        "highlight",
    ]

    inlines = [
        CollectionLinkInline,
    ]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.added_by = request.user
        super(CollectionAdmin, self).save_model(request, obj, form, change)
