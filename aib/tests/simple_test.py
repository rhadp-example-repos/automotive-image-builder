import pytest
from unittest.mock import MagicMock, patch

from aib.simple import without, parse_size, Contents, QMContents, ExtraInclude


@pytest.mark.parametrize(
    "orig,key,res",
    [
        ({"a": 17, "b": 42}, "b", {"a": 17}),
        ({"a": 17, "b": 42}, "a", {"b": 42}),
    ],
)
def test_without(orig, key, res):
    assert without(orig, key) == res


@pytest.mark.parametrize(
    "s,res",
    [
        ("2kB", 1000 * 2),
        ("2KiB", 1024 * 2),
        ("2MB", 1000 * 1000 * 2),
        ("2MiB", 1024 * 1024 * 2),
        ("2GB", 1000 * 1000 * 1000 * 2),
        ("2GiB", 1024 * 1024 * 1024 * 2),
        ("2TB", 1000 * 1000 * 1000 * 1000 * 2),
        ("2TiB", 1024 * 1024 * 1024 * 1024 * 2),
    ],
)
def test_parse_string(s, res):
    assert parse_size(s) == res
