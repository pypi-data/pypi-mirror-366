from json import load
from random import choice
from urllib.request import urlopen

from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import escape, strip_tags
from django.utils.translation import activate, get_language
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django_filters.views import FilterView

from share_links.apps.share_links_comments.models import CommentwithCaptcha
from share_links.conf import PAGINATION_SIZE, SEARCH_MIN_LENGTH, SHOW_WEBARCHIVE_LINK

from .filters import CollectionFilter, LinkFilter, TagsFilter
from .forms import SearchForm
from .models import AboutContactPages, Category, Collection, Link, Tag
from .utils import get_lang, get_title


class SearchView(TemplateView):
    template_name = "share_links/search/results.html"
    context_object_name = "links_list"

    def get_context_data(self, **kwargs):
        activate(get_language())
        context = super().get_context_data(**kwargs)
        context["request_min_chars"] = SEARCH_MIN_LENGTH

        if self.request.method == "GET":
            form = SearchForm(self.request.GET)
            if (
                form.is_valid()
                and len(form.cleaned_data["search"])  # noqa
                >= SEARCH_MIN_LENGTH  # noqa
            ):
                context["links"] = self.get_links_list(
                    form.cleaned_data["search"].lower()
                )
                context["tags"] = self.get_tags_list(self.request.GET["search"].lower())
                return context

        return context

    def get_links_list(self, request):
        return Link.objects.filter(
            Q(link__icontains=request)  # noqa
            | Q(translations__title__icontains=request)  # noqa
            | Q(translations__description__icontains=request)  # noqa
            | Q(tags__translations__tag__icontains=request)  # noqa
        ).distinct()

    def get_tags_list(self, request):
        return Tag.objects.filter(
            Q(translations__tag__icontains=request)  # noqa
            | Q(translations__description__icontains=request)  # noqa
        ).distinct()


class LinksView(FilterView):
    model = Link
    paginate_by = PAGINATION_SIZE
    template_name = "share_links/link/list.html"
    filterset_class = LinkFilter
    queryset = (
        Link.objects.all()
        .order_by("-id")
        .prefetch_related(
            "tags",
            "translations",
            "tags__translations",
            "comments",
            "added_by",
        )
    )


class LinkView(DetailView):
    model = Link
    template_name = "share_links/link/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["show_webarchive_link"] = SHOW_WEBARCHIVE_LINK
        return context


class LinkIndexView(FilterView):
    model = Link
    paginate_by = PAGINATION_SIZE
    template_name = "share_links/link/list.html"
    filterset_class = LinkFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            _("All links for domain") + f" <i>{self.kwargs['domain_name']}</i>"
        )
        return context


def go_random_link(request):
    links = list(Link.objects.all())
    if len(links):
        return redirect(choice(links).link)
    else:
        return redirect("homepage")


class TagsView(FilterView):
    model = Tag
    paginate_by = PAGINATION_SIZE
    template_name = "share_links/tag/list.html"
    filterset_class = TagsFilter


class TagView(ListView):
    model = Link
    paginate_by = PAGINATION_SIZE
    template_name = "share_links/tag/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = Tag.objects.get(translations__slug=self.kwargs["slug"])
        return context

    def get_queryset(self):
        return Link.objects.filter(
            tags__translations__slug__contains=self.kwargs["slug"]
        ).order_by("-date_added")


class CategoryView(DetailView):
    model = Category
    paginate_by = PAGINATION_SIZE
    template_name = "share_links/category/detail.html"


class StatsView(TemplateView):
    template_name = "share_links/misc/stats.html"

    def get_stats(self):
        all_links = Link.objects.count()
        most_used_tag = {"nb": 0, "tag": None}
        for tag in Tag.objects.all().prefetch_related("links"):
            nb = tag.links.count()
            if nb > most_used_tag["nb"]:
                most_used_tag = {"nb": nb, "tag": tag}
        authors = {}
        for author in get_user_model().objects.all():
            authors[author.username] = len(Link.objects.filter(added_by=author))
        languages_list = list(
            Link.objects.values_list("language")
            .distinct()
            .annotate(nb=Count("language"))
            .order_by("-nb")
        )
        languages = {}
        languages_total = 0
        for language in languages_list:
            if language[0] is not None:
                languages[language[0]] = language[1]
                languages_total = languages_total + int(language[1])
        languages["not defined"] = all_links - languages_total
        return {
            "nb_links": all_links,
            "nb_comments": CommentwithCaptcha.objects.all().count(),
            "nb_tags": Tag.objects.count(),
            "most_used_tag": most_used_tag,
            "authors": authors,
            "languages": languages,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = self.get_stats()
        return context


class WebRingView(TemplateView):
    template_name = "share_links/misc/webring.html"

    def get_webring(self):
        webring_json = load(
            urlopen("https://gitlab.com/sodimel/share-links/-/raw/main/webring.json")
        )
        return webring_json

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["webring"] = self.get_webring()

        own_instance = next(
            (
                index
                for (index, dictionnary) in enumerate(context["webring"])
                if self.request.site.domain in dictionnary["url"]
            ),
            None,
        )

        if own_instance is not None:
            context["previous"] = context["webring"][
                (own_instance - 1) % len(context["webring"])
            ]
            context["next"] = context["webring"][
                (own_instance + 1) % len(context["webring"])
            ]
        context["random"] = choice(context["webring"])
        return context


def get_title_view(request):
    data = {"status": "", "title": ""}
    if "url" in request.GET:
        status, text = get_title(request.GET["url"])
        if status is True:
            data["title"] = text
            data["status"] = "ok"
        else:
            data["title"] = ""
            data["status"] = text
    else:
        data["title"] = ""
        data["status"] = _("Error: no url supplied.")
    return JsonResponse(data)


def get_lang_view(request):
    data = {"status": "", "lang": ""}
    if "url" in request.GET:
        status, text = get_lang(request.GET["url"])
        if status is True:
            data["lang"] = text
            data["status"] = "ok"
        else:
            data["lang"] = ""
            data["status"] = text
    else:
        data["lang"] = ""
        data["status"] = _("Error: no url supplied.")
    return JsonResponse(data)


class AboutView(TemplateView):
    template_name = "share_links/misc/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["about_text"] = AboutContactPages.objects.first()
        return context


class ContactView(TemplateView):
    template_name = "share_links/misc/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_text"] = AboutContactPages.objects.last()
        return context


class RSSView(TemplateView):
    template_name = "share_links/rss/home.html"


def get_description(item, display_type=False):
    activate(get_language())

    long_description = strip_tags(item.description)
    description = " ".join(long_description.split(" ")[:20])
    if len(description) < len(long_description):
        description += "..."

    if display_type:
        if type(item) is Link:
            return f"(link) - {description}"
        return f"(tag) - {description}"
    return description


class RSSNewView(Feed):
    title = _("New links & tags")
    link = "/all/"
    description = _("Creation of links and tags.")

    def items(self):
        links = list(Link.objects.order_by("-id")[:5])
        tags = list(Tag.objects.order_by("-id")[:5])
        links_tags = links + tags
        links_tags.sort(key=lambda r: r.date_added, reverse=True)
        return links_tags[:5]

    def item_title(self, item):
        if type(item) is Link:
            if item.title:
                return escape(str(item.title))
            return escape(str(item.link))
        return escape(str(item.tag))

    def item_description(self, item):
        return get_description(item, display_type=True)

    def item_link(self, item):
        if type(item) is Link:
            return reverse("link", args=[item.pk])
        return reverse("tag", args=[item.slug])

    def item_pubdate(self, item):
        return item.date_added

    def item_unique_id(self, item):
        return item.pk

    def item_categories(self, item):
        if type(item) is Link:
            return "link"
        return "tag"


class RSSNewLinksView(Feed):
    title = _("New links")
    link = "/links/"
    description = _("Creation of links.")

    def items(self):
        return Link.objects.order_by("-id")[:5]

    def item_title(self, item):
        if item.title:
            return escape(str(item.title))
        return escape(str(item.link))

    def item_description(self, item):
        return get_description(item)

    def item_link(self, item):
        return reverse("link", args=[item.pk])

    def item_pubdate(self, item):
        return item.date_added

    def item_unique_id(self, item):
        return item.pk

    def item_categories(self, item):
        return "link"


class RSSNewTagsView(Feed):
    title = _("New tags")
    link = "/tags/"
    description = _("Creation of tags.")

    def items(self):
        return Tag.objects.order_by("-id")[:5]

    def item_title(self, item):
        return escape(str(item.tag))

    def item_description(self, item):
        return get_description(item)

    def item_link(self, item):
        return reverse("tag", args=[item.slug])

    def item_pubdate(self, item):
        return item.date_added

    def item_unique_id(self, item):
        return item.pk

    def item_categories(self, item):
        return "tag"


class CollectionsView(FilterView):
    model = Collection
    paginate_by = PAGINATION_SIZE
    template_name = "share_links/collection/list.html"
    filterset_class = CollectionFilter

    def get_queryset(self):
        if self.request.GET.get("sort", False):
            sort = self.request.GET.get("sort", False)
            if sort == "new":
                objects = Collection.objects.all().order_by("-id")
            if sort == "old":
                objects = Collection.objects.all().order_by("id")
            if sort == "highlight":
                objects = Collection.objects.filter(highlight=True).order_by("-id")
        else:
            objects = Collection.objects.all().order_by("-id")
        return objects


class CollectionView(ListView):
    model = Collection
    paginate_by = PAGINATION_SIZE
    template_name = "share_links/collection/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collection"] = Collection.objects.get(
            translations__slug=self.kwargs["slug"]
        )
        return context
