from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.utils.translation import gettext as _


class OnlineOfflineFilter(SimpleListFilter):
    title = _("is online?")
    parameter_name = "online"

    def lookups(self, request, model_admin):
        return [
            ("online", _("Online")),
            ("offline", _("Offline")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "online":
            return queryset.filter(online=True)
        if self.value():
            return queryset.filter(online=False)


class HasAtLeastOneTagFilter(SimpleListFilter):
    title = _("has at least one tag")
    parameter_name = "one_tag"

    def lookups(self, request, model_admin):
        return [
            ("one_tag", _("At least one tag")),
            ("no_tag", _("No tag")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "one_tag":
            return queryset.annotate(num_tags=Count("tags")).filter(num_tags__gt=0)
        if self.value():
            return queryset.annotate(num_tags=Count("tags")).filter(num_tags__lt=1)


class RandomFilter(SimpleListFilter):
    title = _("random")
    parameter_name = "random"

    def lookups(self, request, model_admin):
        return [
            ("random", _("Random")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "random":
            return queryset.order_by("?")
