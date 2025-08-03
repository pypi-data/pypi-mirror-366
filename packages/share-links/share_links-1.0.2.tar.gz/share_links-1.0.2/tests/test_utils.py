# tests/test_utils.py

import pytest

from share_links.utils import get_full_url, get_lang, get_request, get_title, iri2uri


@pytest.mark.django_db
def test_iri2uri():
    iri = "http://example.com/é"
    expected_uri = "http://example.com/%C3%A9"
    assert iri2uri(iri) == expected_uri


@pytest.mark.django_db
def test_get_full_url():
    url = "http://example.com/é"
    expected_full_url = "http://example.com/%25C3%25A9"
    assert get_full_url(url) == expected_full_url


@pytest.mark.django_db
def test_get_request():
    url = "http://example.com"
    request = get_request(url)
    assert request.get_header("User-agent").startswith("share-links v")


@pytest.mark.django_db
def test_get_title_success(monkeypatch):
    def mock_urlopen(*args, **kwargs):
        class MockResponse:
            def read(self):
                return b"<html><head><title>Test Title</title></head></html>"

        return MockResponse()

    monkeypatch.setattr("share_links.utils.urlopen", mock_urlopen)

    url = "http://example.com"
    status, title = get_title(url)
    assert status is True
    assert title == "Test Title"


@pytest.mark.django_db
def test_get_title_empty(monkeypatch):
    def mock_urlopen(*args, **kwargs):
        class MockResponse:
            def read(self):
                return b"<html><head></head></html>"

        return MockResponse()

    monkeypatch.setattr("share_links.utils.urlopen", mock_urlopen)

    url = "http://example.com"
    status, title = get_title(url)
    assert status is False
    assert title == "Got an empty title, you'll need to be creative!"


@pytest.mark.django_db
def test_get_lang_success(monkeypatch):
    def mock_urlopen(*args, **kwargs):
        class MockResponse:
            def read(self):
                return b"<html lang='en'><head></head></html>"

        return MockResponse()

    monkeypatch.setattr("share_links.utils.urlopen", mock_urlopen)

    url = "http://example.com"
    status, lang = get_lang(url)
    assert status is True
    assert lang == "en"


@pytest.mark.django_db
def test_get_lang_not_found(monkeypatch):
    def mock_urlopen(*args, **kwargs):
        class MockResponse:
            def read(self):
                return b"<html><head></head></html>"

        return MockResponse()

    monkeypatch.setattr("share_links.utils.urlopen", mock_urlopen)

    url = "http://example.com"
    status, lang = get_lang(url)
    assert status is False
    assert lang == "Cannot find a lang attribute."
