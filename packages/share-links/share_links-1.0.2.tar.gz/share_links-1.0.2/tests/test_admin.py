# tests/test_admin.py

import pytest
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.utils.translation import activate

from share_links.admin import (
    AboutContactPagesAdmin,
    CategoryAdmin,
    CollectionAdmin,
    LinkAdmin,
    TagAdmin,
)
from share_links.models import AboutContactPages, Category, Collection, Link, Tag


@pytest.mark.django_db
def test_about_contact_pages_admin_name():
    about_page = AboutContactPages.objects.create()
    contact_page = AboutContactPages.objects.create()

    request = RequestFactory().get("/")  # noqa: F841
    admin_site = AdminSite()
    admin = AboutContactPagesAdmin(AboutContactPages, admin_site)

    assert admin.name(about_page) == "About page"
    assert admin.name(contact_page) == "Contact page"


@pytest.mark.django_db
def test_about_contact_pages_admin_save_delete_msg():
    request = RequestFactory().get("/")
    request.user = "testuser"
    setattr(request, "session", "session")
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)

    admin_site = AdminSite()
    admin = AboutContactPagesAdmin(AboutContactPages, admin_site)

    assert admin.save_delete_msg(request) is False
    assert len(messages) == 1


@pytest.mark.django_db
def test_about_contact_pages_admin_save_model():
    request = RequestFactory().get("/")
    setattr(request, "session", "session")
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)

    admin_site = AdminSite()
    admin = AboutContactPagesAdmin(AboutContactPages, admin_site)

    obj = AboutContactPages()
    form = None
    change = False

    # Test saving when there are already two instances
    AboutContactPages.objects.create()
    AboutContactPages.objects.create()
    assert admin.save_model(request, obj, form, change) is False
    assert len(messages) == 1

    # Test saving when there are less than two instances
    AboutContactPages.objects.all().delete()
    admin.save_model(request, obj, form, change)
    assert AboutContactPages.objects.count() == 1


@pytest.mark.django_db
def test_link_admin_file_exist():
    link = Link.objects.create(link="https://example.com", file="example.pdf")

    request = RequestFactory().get("/")  # noqa: F841
    admin_site = AdminSite()
    admin = LinkAdmin(Link, admin_site)

    assert admin.file_exist(link) is True


@pytest.mark.django_db
def test_link_admin_title_sortable():
    link = Link.objects.create(link="https://example.com", title="Example Title")

    request = RequestFactory().get("/")  # noqa: F841
    admin_site = AdminSite()
    admin = LinkAdmin(Link, admin_site)

    assert admin.title_sortable(link) == "Example Title"


@pytest.mark.django_db
def test_link_admin_webarchive_url():
    link = Link.objects.create(link="https://example.com")

    request = RequestFactory().get("/")  # noqa: F841
    admin_site = AdminSite()
    admin = LinkAdmin(Link, admin_site)

    assert (
        admin.webarchive_url(link)
        == '<a href="https://web.archive.org/save/https://example.com" target="_blank">Save this</a>'
    )


@pytest.mark.django_db
def test_link_admin_view_link():
    link = Link.objects.create(link="https://example.com")

    request = RequestFactory().get("/")  # noqa: F841
    admin_site = AdminSite()
    admin = LinkAdmin(Link, admin_site)

    assert admin.view_link(link) == f'<a href="/en/link/{link.id}/">View</a>'


@pytest.mark.django_db
def test_tag_admin_link_nb():
    tag = Tag.objects.create(tag="Example Tag")
    link = Link.objects.create(link="https://example.com")
    link.tags.add(tag)

    request = RequestFactory().get("/")  # noqa: F841
    admin_site = AdminSite()
    admin = TagAdmin(Tag, admin_site)

    assert admin.link_nb(tag) == 1


@pytest.mark.django_db
def test_category_admin_tag_nb():
    category = Category.objects.create(label="Example Category")
    tag = Tag.objects.create(tag="Example Tag", category=category)  # noqa: F841

    request = RequestFactory().get("/")  # noqa: F841
    admin_site = AdminSite()
    admin = CategoryAdmin(Category, admin_site)

    assert admin.tag_nb(category) == 1


@pytest.mark.django_db
def test_collection_admin_save_model():
    activate("en")

    User = get_user_model()
    user = User.objects.create(username="testuser")

    request = RequestFactory().get("/")
    request.user = user
    setattr(request, "session", "session")
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)

    admin_site = AdminSite()
    admin = CollectionAdmin(Collection, admin_site)

    # Create a Collection object with a translation
    obj = Collection()
    obj.name = "Test Collection"
    obj.added_by = user
    obj.save()

    form = None
    change = False

    admin.save_model(request, obj, form, change)
    assert obj.added_by == user
    assert Collection.objects.count() == 1
