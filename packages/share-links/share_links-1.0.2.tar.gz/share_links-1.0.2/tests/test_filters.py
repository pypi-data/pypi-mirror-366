# tests/test_filters.py

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory
from django.utils import timezone

from share_links.filters import CollectionFilter, LinkFilter, TagsFilter
from share_links.models import Collection, Link, Tag


@pytest.mark.django_db
def test_link_filter_highlight():
    Link.objects.create(link="https://example1.com", highlight=True)
    Link.objects.create(link="https://example2.com", highlight=False)

    request = RequestFactory().get("/", {"highlight": "True"})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = LinkFilter(request=request, queryset=Link.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().highlight is True


@pytest.mark.django_db
def test_link_filter_added_by():
    User = get_user_model()
    user1 = User.objects.create(username="user1")
    user2 = User.objects.create(username="user2")
    Link.objects.create(link="https://example1.com", added_by=user1)
    Link.objects.create(link="https://example2.com", added_by=user2)

    request = RequestFactory().get("/", {"added_by": user1.id})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = LinkFilter(request=request, queryset=Link.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().added_by == user1


@pytest.mark.django_db
def test_link_filter_date_added():
    Link.objects.create(
        link="https://example1.com",
        date_added=timezone.now() - timezone.timedelta(days=1),
    )
    Link.objects.create(link="https://example2.com", date_added=timezone.now())

    request = RequestFactory().get(
        "/", {"date_added_after": timezone.now() - timezone.timedelta(days=2)}
    )
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = LinkFilter(request=request, queryset=Link.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2


@pytest.mark.django_db
def test_link_filter_language():
    Link.objects.create(link="https://example1.com", language="en")
    Link.objects.create(link="https://example2.com", language="fr")

    request = RequestFactory().get("/", {"language": "en"})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = LinkFilter(request=request, queryset=Link.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().language == "en"


@pytest.mark.django_db
def test_link_filter_online():
    Link.objects.create(link="https://example1.com", online=True)
    Link.objects.create(link="https://example2.com", online=False)

    request = RequestFactory().get("/", {"online": "True"})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = LinkFilter(request=request, queryset=Link.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().online is True


@pytest.mark.django_db
def test_link_filter_comments():
    site, created = Site.objects.get_or_create(id=1)

    link_with_comments = Link.objects.create(link="https://example1.com")
    link_with_comments.comments.create(comment="Test comment", site=site)
    Link.objects.create(link="https://example2.com")

    request = RequestFactory().get("/", {"comments": "True"})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = LinkFilter(request=request, queryset=Link.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().comments.exists()


@pytest.mark.django_db
def test_collection_filter_highlight():
    Collection.objects.create(name="Collection1", highlight=True)
    Collection.objects.create(name="Collection2", highlight=False)

    request = RequestFactory().get("/", {"highlight": "True"})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = CollectionFilter(
        request=request, queryset=Collection.objects.all()
    )

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().highlight is True


@pytest.mark.django_db
def test_collection_filter_added_by():
    User = get_user_model()
    user1 = User.objects.create(username="user1")
    user2 = User.objects.create(username="user2")
    Collection.objects.create(name="Collection1", added_by=user1)
    Collection.objects.create(name="Collection2", added_by=user2)

    request = RequestFactory().get("/", {"added_by": user1.id})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = CollectionFilter(
        request=request, queryset=Collection.objects.all()
    )

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().added_by == user1


@pytest.mark.django_db
def test_collection_filter_date_added():
    Collection.objects.create(
        name="Collection1", date_added=timezone.now() - timezone.timedelta(days=1)
    )
    Collection.objects.create(name="Collection2", date_added=timezone.now())

    request = RequestFactory().get(
        "/", {"date_added_after": timezone.now() - timezone.timedelta(days=2)}
    )
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = CollectionFilter(
        request=request, queryset=Collection.objects.all()
    )

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2


@pytest.mark.django_db
def test_tags_filter_highlight():
    Tag.objects.create(tag="Tag1", highlight=True)
    Tag.objects.create(tag="Tag2", highlight=False)

    request = RequestFactory().get("/", {"highlight": "True"})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = TagsFilter(request=request, queryset=Tag.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().highlight is True


@pytest.mark.django_db
def test_tags_filter_name():
    Tag.objects.create(tag="Tag1")
    Tag.objects.create(tag="Tag2")

    request = RequestFactory().get("/", {"name": "Tag1"})
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = TagsFilter(request=request, queryset=Tag.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
    assert filtered_queryset.first().tag == "Tag1"


@pytest.mark.django_db
def test_tags_filter_date_added():
    Tag.objects.create(
        tag="Tag1", date_added=timezone.now() - timezone.timedelta(days=1)
    )
    Tag.objects.create(tag="Tag2", date_added=timezone.now())

    request = RequestFactory().get(
        "/", {"date_added_after": timezone.now() - timezone.timedelta(days=2)}
    )
    request.resolver_match = type("ResolverMatch", (object,), {"kwargs": {}})()

    filter_instance = TagsFilter(request=request, queryset=Tag.objects.all())

    filtered_queryset = filter_instance.qs

    assert filtered_queryset.count() == 2
