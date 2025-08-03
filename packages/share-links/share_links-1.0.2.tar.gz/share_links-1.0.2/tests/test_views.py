# tests/test_views.py

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from share_links.models import AboutContactPages, Category, Collection, Link, Tag


@pytest.mark.django_db
def test_search_view(client):
    Link.objects.create(link="https://example.com", title="Example Title")

    response = client.get(reverse("search"), {"search": "example"})
    assert response.status_code == 200
    assert "links" in response.context
    assert "tags" in response.context


@pytest.mark.django_db
def test_links_view(client):
    Link.objects.create(link="https://example.com", title="Example Title")

    response = client.get(reverse("homepage"))
    assert response.status_code == 200
    assert "object_list" in response.context


@pytest.mark.django_db
def test_link_view(client):
    link = Link.objects.create(link="https://example.com", title="Example Title")

    response = client.get(reverse("link", args=[link.pk]))
    assert response.status_code == 200
    assert "object" in response.context


@pytest.mark.django_db
def test_link_index_view(client):
    Link.objects.create(link="https://example.com", title="Example Title")

    response = client.get(reverse("link_index", kwargs={"domain_name": "example.com"}))
    assert response.status_code == 200
    assert "object_list" in response.context


@pytest.mark.django_db
def test_tags_view(client):
    Tag.objects.create(tag="Example Tag")

    response = client.get(reverse("tags"))
    assert response.status_code == 200
    assert "object_list" in response.context


@pytest.mark.django_db
def test_tag_view(client):
    tag = Tag.objects.create(tag="Example Tag")
    link = Link.objects.create(link="https://example.com", title="Example Title")
    link.tags.add(tag)

    response = client.get(reverse("tag", args=[tag.slug]))
    assert response.status_code == 200
    assert "object_list" in response.context


@pytest.mark.django_db
def test_category_view(client):
    category = Category.objects.create(label="Example Category")

    response = client.get(reverse("category", args=[category.pk]))
    assert response.status_code == 200
    assert "object" in response.context


@pytest.mark.django_db
def test_stats_view(client):
    Link.objects.create(link="https://example.com", title="Example Title")

    response = client.get(reverse("stats"))
    assert response.status_code == 200
    assert "stats" in response.context


@pytest.mark.django_db
def test_webring_view(client):
    response = client.get(reverse("webring"))
    assert response.status_code == 200
    assert "webring" in response.context


@pytest.mark.django_db
def test_get_title_view(client):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="testpass")
    client.force_login(user)

    response = client.get(reverse("get_title"), {"url": "https://example.com"})
    assert response.status_code == 200
    assert "status" in response.json()
    assert "title" in response.json()


@pytest.mark.django_db
def test_get_lang_view(client):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="testpass")
    client.force_login(user)

    response = client.get(reverse("get_lang"), {"url": "https://example.com"})
    assert response.status_code == 200
    assert "status" in response.json()
    assert "lang" in response.json()


@pytest.mark.django_db
def test_about_view(client):
    AboutContactPages.objects.create(page_title="About Page")

    response = client.get(reverse("about"))
    assert response.status_code == 200
    assert "about_text" in response.context


@pytest.mark.django_db
def test_contact_view(client):
    AboutContactPages.objects.create(page_title="Contact Page")

    response = client.get(reverse("contact"))
    assert response.status_code == 200
    assert "contact_text" in response.context


@pytest.mark.django_db
def test_rss_new_view(client):
    Link.objects.create(link="https://example.com", title="Example Title")

    response = client.get(reverse("rss_new"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_rss_new_links_view(client):
    Link.objects.create(link="https://example.com", title="Example Title")

    response = client.get(reverse("rss_new_links"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_rss_new_tags_view(client):
    Tag.objects.create(tag="Example Tag")

    response = client.get(reverse("rss_new_tags"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_collections_view(client):
    Collection.objects.create(name="Example Collection")

    response = client.get(reverse("collections"))
    assert response.status_code == 200
    assert "object_list" in response.context


@pytest.mark.django_db
def test_collection_view(client):
    collection = Collection.objects.create(name="Example Collection")

    response = client.get(reverse("collection", args=[collection.slug]))
    assert response.status_code == 200
    assert "object_list" in response.context
