from django.conf.global_settings import LANGUAGES as FULL_LANGUAGES_LIST
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Count, FileField
from django.forms.fields import CheckboxInput
from django.utils.translation import gettext_lazy as _
from django_filters import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    DateRangeFilter,
    FilterSet,
    ModelChoiceFilter,
)

from .models import Collection, Link, Tag

languages_dict = dict(FULL_LANGUAGES_LIST)


class LinkFilter(FilterSet):
    highlight = BooleanFilter(
        field_name="highlight", label=_("Highlighted"), widget=CheckboxInput
    )
    added_by = ModelChoiceFilter(
        field_name="added_by",
        label=_("Added by"),
        queryset=get_user_model().objects.all(),
    )
    date_added = DateRangeFilter(field_name="date_added", label=_("Date added"))
    language = ChoiceFilter(
        field_name="language",
        label=_("Language"),
        # choices=get_languages_list,  # moved in __init__!
    )
    online = BooleanFilter(field_name="online", label=_("Is online"))
    comments = BooleanFilter(field_name="comments", label=_("Has comments"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # get choices with queryset based on request parameter (view name/domain name if present)
        if "domain_name" in self.request.resolver_match.kwargs:
            self.filters["language"].extra["choices"] = self.get_languages_list(
                self.request.resolver_match.kwargs["domain_name"]
            )
        else:
            self.filters["language"].extra["choices"] = self.get_languages_list()

    def get_languages_list(self, domain_name=None, *args, **kwargs):
        if domain_name:
            languages = (
                Link.objects.filter(link__contains=domain_name)
                .values("language")
                .distinct()
                .annotate(total=Count("id"))
                .order_by("-total")
            )
        else:
            languages = (
                Link.objects.all()
                .values("language")
                .distinct()
                .annotate(total=Count("id"))
                .order_by("-total")
            )

        languages_choices = []
        for language in languages:
            if language["language"] in languages_dict:
                language_txt = f"{_(languages_dict[language['language']])} ({str(language['total'])})"
                languages_choices.append((language["language"], language_txt))
            elif language["language"] is None:
                languages_choices.append(
                    ("null", _("No language") + " (" + str(language["total"]) + ")")
                )

        return languages_choices

    class Meta:
        model = Link

        fields = [
            "highlight",
            "language",
            "online",
            "added_by",
            "date_added",
            "comments",
        ]

        exclude = ["allow_override_title", "allow_override_language"]

        filter_overrides = {
            # FileField: {
            #     "filter_class": BooleanFilter,
            #     "extra": lambda f: {
            #         "lookup_expr": "not__isnull",
            #     }
            # },
            GenericRelation: {
                "filter_class": BooleanFilter,
                "extra": lambda f: {
                    "lookup_expr": "not__isnull",
                },
            },
            FileField: {
                "filter_class": BooleanFilter,
                "extra": lambda f: {
                    "lookup_expr": "not__isnull",
                },
            },
        }


class CollectionFilter(FilterSet):
    highlight = BooleanFilter(
        field_name="highlight", label=_("Highlighted"), widget=CheckboxInput
    )
    added_by = ModelChoiceFilter(
        field_name="added_by",
        label=_("Added by"),
        queryset=get_user_model().objects.all(),
    )
    date_added = DateRangeFilter(field_name="date_added", label=_("Date added"))

    class Meta:
        model = Collection

        fields = [
            "highlight",
            "added_by",
            "date_added",
        ]


class TagsFilter(FilterSet):
    highlight = BooleanFilter(
        field_name="highlight", label=_("Highlighted"), widget=CheckboxInput
    )
    name = CharFilter(
        field_name="translations__tag", label=_("Tag name"), lookup_expr="icontains"
    )
    date_added = DateRangeFilter(field_name="date_added", label=_("Date added"))

    class Meta:
        model = Tag

        fields = [
            "name",
            "highlight",
            "date_added",
        ]
