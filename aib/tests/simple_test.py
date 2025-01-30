import pytest
import unittest
from unittest.mock import MagicMock, patch

import aib
from aib.simple import (
    without,
    parse_size,
    Contents,
    QMContents,
    ExtraInclude,
    ManifestLoader,
)


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


def test_parse_unsupported_string():
    """
    Cover negative case for parse_string
    """
    with pytest.raises(TypeError):
        parse_size("2Kg")


class TestManifestLoader(unittest.TestCase):
    def load_manifest(self, manifest, use_fusa=False):
        defines = {
            "_basedir": "",
            "_workdir": "",
            "arch": "x86_64",
            "use_fusa": use_fusa,
        }

        loader = ManifestLoader(defines)
        loader._load(manifest, "test", "/tmp")
        return loader

    def test_basic(self):
        with self.assertRaises(aib.exceptions.SimpleManifestParseError):
            self.load_manifest({})  # Name is required
        self.load_manifest({"name": "foo"})

    def test_fusa(self):
        self.load_manifest(
            {
                "name": "foo",
                "content": {
                    "container_images": [
                        {
                            "source": "registry.gitlab.com/centos/automotive/sample-images/demo/auto-apps",
                            "tag": "latest",
                            "name": "localhost/auto-apps",
                        }
                    ]
                },
            },
            use_fusa=True,
        )
        with self.assertRaisesRegex(aib.exceptions.SimpleManifestParseError, "--fusa"):
            self.load_manifest(
                {
                    "name": "foo",
                    "content": {
                        "container_images": [
                            {
                                "source": "registry.gitlab.com/centos/automotive/sample-images/demo/auto-apps",
                                "tag": "latest",
                                "name": "localhost/auto-apps",
                                "containers-transport": "containers-storage",
                            }
                        ]
                    },
                },
                use_fusa=True,
            )

    # Validate that our jsonschema default expension code works
    def test_default_expand(self):
        loader = self.load_manifest(
            {
                "name": "foo",
                "content": {
                    "container_images": [
                        {
                            "source": "registry.gitlab.com/centos/automotive/sample-images/demo/auto-apps",
                            # This should expend the default for tag to label
                        }
                    ]
                },
            }
        )
        containers = loader.defines["simple_containers"]
        self.assertEqual(len(containers), 1)
        self.assertIn("tag", containers[0])
        self.assertEqual(containers[0]["tag"], "latest")
