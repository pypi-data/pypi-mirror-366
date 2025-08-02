import pytest
from pydantic import SecretStr

from homelab_config.utils import parse_consul_url
from homelab_config.utils import parse_consul_urls
from homelab_config.utils import split_url_list


# Test data
SINGLE_URL = "http://example.com"
MULTIPLE_URLS = "http://example.com, https://backup.com"
URLS_WITH_SPACES = "  http://example.com ,  https://backup.com  "
URLS_WITH_EMPTY = "http://example.com,,https://backup.com,"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("", []),
        (None, []),
        (SINGLE_URL, ["http://example.com"]),
        (MULTIPLE_URLS, ["http://example.com", "https://backup.com"]),
        (URLS_WITH_SPACES, ["http://example.com", "https://backup.com"]),
        (URLS_WITH_EMPTY, ["http://example.com", "https://backup.com"]),
    ],
)
def test_split_url_list(test_input, expected):
    """Test split_url_list with various inputs."""
    if test_input is None:
        assert split_url_list("") == expected
    else:
        assert split_url_list(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, []),
        (SINGLE_URL, ["http://example.com"]),
        (SecretStr(SINGLE_URL), ["http://example.com"]),
        ([SINGLE_URL, SecretStr(MULTIPLE_URLS)], ["http://example.com", "http://example.com", "https://backup.com"]),
        (SecretStr("http://example.com\nhttp://backup.com"), ["http://example.com", "http://backup.com"]),
    ],
)
def test_parse_consul_urls(test_input, expected):
    """Test parse_consul_urls with various input types."""
    assert parse_consul_urls(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("http://localhost:8500", {"host": "localhost", "port": 8500, "scheme": "http"}),
        ("https://consul.example.com", {"host": "consul.example.com", "port": 443, "scheme": "https"}),
    ],
)
def test_parse_consul_url_valid(test_input, expected):
    """Test parse_consul_url with valid URLs."""
    assert parse_consul_url(test_input) == expected


@pytest.mark.parametrize(
    "test_input,error_msg",
    [
        ("invalid://", "URL parsing failed"),
        ("http://localhost:invalid", "URL parsing failed"),
        ("not_a_url", "URL parsing failed"),
        ("", "URL parsing failed"),
        ("http://", "URL parsing failed"),
        ("http://:8500", "URL parsing failed"),
    ],
)
def test_parse_consul_url_invalid(test_input, error_msg):
    """Test parse_consul_url with invalid URLs."""
    with pytest.raises(ValueError) as excinfo:
        parse_consul_url(test_input)
    assert str(excinfo.value).startswith(error_msg)
