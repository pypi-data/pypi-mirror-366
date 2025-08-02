import pytest

from share_links.models import Category, Collection, CollectionLink, Link, Tag


@pytest.mark.django_db
def test_link_creation():
    link = Link.objects.create(
        link="https://example.com",
        title="Example Title",
        description="Example Description",
        highlight=True,
        online=True,
        added_by=None,
        language="en",
        allow_override_title=True,
        allow_override_language=True,
    )
    assert link.link == "https://example.com"
    assert link.title == "Example Title"
    assert link.description == "Example Description"
    assert link.highlight is True
    assert link.online is True
    assert link.language == "en"
    assert link.allow_override_title is True
    assert link.allow_override_language is True


@pytest.mark.django_db
def test_link_save_with_weasyprint():
    link = Link.objects.create(
        link="https://example.com",
        title="Example Title",
        description="Example Description",
        highlight=True,
        online=True,
        added_by=None,
        language="en",
        allow_override_title=True,
        allow_override_language=True,
        save_file=True,
    )
    link.save()
    assert link.file is not None


@pytest.mark.django_db
def test_link_str_method():
    link = Link.objects.create(
        link="https://example.com",
        title="Example Title",
        description="Example Description",
    )
    assert str(link) == "Example Title (https://example.com)"

    link.title = None
    assert str(link) == "None (https://example.com)"


@pytest.mark.django_db
def test_category_creation():
    category = Category.objects.create(
        label="Example Category", description="Example Description"
    )
    assert category.label == "Example Category"
    assert category.description == "Example Description"


@pytest.mark.django_db
def test_category_str_method():
    category = Category.objects.create(
        label="Example Category", description="Example Description"
    )
    assert str(category) == "Example Category"


@pytest.mark.django_db
def test_tag_creation():
    tag = Tag.objects.create(
        tag="Example Tag", description="Example Description", highlight=True
    )
    assert tag.tag == "Example Tag"
    assert tag.description == "Example Description"
    assert tag.highlight is True


@pytest.mark.django_db
def test_tag_slug_creation():
    tag = Tag.objects.create(tag="Example Tag", description="Example Description")
    assert tag.slug == "example-tag"


@pytest.mark.django_db
def test_tag_str_method():
    tag = Tag.objects.create(tag="Example Tag", description="Example Description")
    assert str(tag) == "Example Tag"


@pytest.mark.django_db
def test_collection_creation():
    collection = Collection.objects.create(
        name="Example Collection", description="Example Description", highlight=True
    )
    assert collection.name == "Example Collection"
    assert collection.description == "Example Description"
    assert collection.highlight is True


@pytest.mark.django_db
def test_collection_slug_creation():
    collection = Collection.objects.create(
        name="Example Collection", description="Example Description"
    )
    assert collection.slug == "example-collection"


@pytest.mark.django_db
def test_collection_str_method():
    collection = Collection.objects.create(
        name="Example Collection", description="Example Description"
    )
    assert str(collection) == "Example Collection"


@pytest.mark.django_db
def test_collection_link_creation():
    link = Link.objects.create(
        link="https://example.com",
        title="Example Title",
        description="Example Description",
    )
    collection = Collection.objects.create(
        name="Example Collection", description="Example Description"
    )
    collection_link = CollectionLink.objects.create(
        link=link, collection=collection, description="Example Description"
    )
    assert collection_link.link == link
    assert collection_link.collection == collection
    assert collection_link.description == "Example Description"


@pytest.mark.django_db
def test_collection_link_str_method():
    link = Link.objects.create(
        link="https://example.com",
        title="Example Title",
        description="Example Description",
    )
    collection = Collection.objects.create(
        name="Example Collection", description="Example Description"
    )
    collection_link = CollectionLink.objects.create(
        link=link, collection=collection, description="Example Description"
    )
    assert str(collection_link) == "Example Title"
