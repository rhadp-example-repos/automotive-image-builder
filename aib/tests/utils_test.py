import pytest
import unittest

import aib.utils

class TestManifestLoader(unittest.TestCase):
    def test_yaml_loader(self):
        assert(false)
        utils.yaml_load_ordered("foobar: 12")
