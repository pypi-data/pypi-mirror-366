from django.contrib.auth.decorators import login_required
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django_comments.feeds import LatestCommentFeed

from . import views

urlpatterns = [
    # search
    path(_("search/"), views.SearchView.as_view(), name="search"),
    # rss
    path(_("rss/"), views.RSSView.as_view(), name="rss_index"),
    path(_("rss/new/all/"), views.RSSNewView(), name="rss_new"),
    path(_("rss/new/links/"), views.RSSNewLinksView(), name="rss_new_links"),
    path(_("rss/new/tags/"), views.RSSNewTagsView(), name="rss_new_tags"),
    path("rss/latest-comments/", LatestCommentFeed()),
    # misc
    path(_("about/"), views.AboutView.as_view(), name="about"),
    path(_("contact/"), views.ContactView.as_view(), name="contact"),
    path(_("statistics/"), views.StatsView.as_view(), name="stats"),
    path(_("webring/"), views.WebRingView.as_view(), name="webring"),
    # smol api
    path(_("get-title/"), login_required(views.get_title_view), name="get_title"),
    path(_("get-lang/"), login_required(views.get_lang_view), name="get_lang"),
    # tags
    path(_("tag/<str:slug>/"), views.TagView.as_view(), name="tag"),
    path(_("tags/"), views.TagsView.as_view(), name="tags"),
    path(_("category/<int:pk>/"), views.CategoryView.as_view(), name="category"),
    # Comments
    # path(_("last-comments/"), views.LastCommentsView.as_view(), name="comments"),
    # collections
    path(
        _("collection/<str:slug>/"), views.CollectionView.as_view(), name="collection"
    ),
    path(_("collections/"), views.CollectionsView.as_view(), name="collections"),
    # links
    path(_("link/<int:pk>/"), views.LinkView.as_view(), name="link"),
    path(
        _("domain-name/<str:domain_name>/"),
        views.LinkIndexView.as_view(),
        name="link_index",
    ),
    path(_("random/"), views.go_random_link, name="random"),
    path("", views.LinksView.as_view(), name="homepage"),
]
