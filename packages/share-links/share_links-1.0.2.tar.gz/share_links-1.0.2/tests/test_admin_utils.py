# tests/test_admin_utils.py

import pytest
from django.contrib.admin import AdminSite
from django.test import RequestFactory

from share_links.admin_utils import (
    HasAtLeastOneTagFilter,
    OnlineOfflineFilter,
    RandomFilter,
)
from share_links.models import Link, Tag


@pytest.mark.django_db
def test_online_offline_filter():
    Link.objects.create(link="https://example1.com", online=True)
    Link.objects.create(link="https://example2.com", online=False)

    request = RequestFactory().get("/")
    queryset = Link.objects.all()

    filter_instance = OnlineOfflineFilter(request, {}, Link, AdminSite())
    filter_instance.value = lambda: "online"
    filtered_queryset = filter_instance.queryset(request, queryset)
    assert filtered_queryset.count() == 1
    assert filtered_queryset.first().online is True

    filter_instance.value = lambda: "offline"
    filtered_queryset = filter_instance.queryset(request, queryset)
    assert filtered_queryset.count() == 1
    assert filtered_queryset.first().online is False


@pytest.mark.django_db
def test_has_at_least_one_tag_filter():
    tag = Tag.objects.create(tag="Test Tag")
    link_with_tag = Link.objects.create(link="https://example1.com")
    link_with_tag.tags.add(tag)
    Link.objects.create(link="https://example2.com")

    request = RequestFactory().get("/")
    queryset = Link.objects.all()

    filter_instance = HasAtLeastOneTagFilter(request, {}, Link, AdminSite())
    filter_instance.value = lambda: "one_tag"
    filtered_queryset = filter_instance.queryset(request, queryset)
    assert filtered_queryset.count() == 1
    assert filtered_queryset.first().tags.count() > 0

    filter_instance.value = lambda: "no_tag"
    filtered_queryset = filter_instance.queryset(request, queryset)
    assert filtered_queryset.count() == 1
    assert filtered_queryset.first().tags.count() == 0


@pytest.mark.django_db
def test_random_filter():
    # Create some test data
    Link.objects.create(link="https://example1.com")
    Link.objects.create(link="https://example2.com")

    request = RequestFactory().get("/")
    queryset = Link.objects.all()

    filter_instance = RandomFilter(request, {}, Link, AdminSite())
    filter_instance.value = lambda: "random"
    filtered_queryset = filter_instance.queryset(request, queryset)
    assert filtered_queryset.count() == 2
    assert all([link in queryset for link in filtered_queryset])
