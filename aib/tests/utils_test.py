import unittest
import collections
from io import StringIO

from aib import utils


class TestManifestLoader(unittest.TestCase):
    def test_ordered_yaml_loader(self):
        res = utils.yaml_load_ordered("foobar: 12")
        self.assertEqual(type(res), collections.OrderedDict)


class TestExtractCommentsHeader(unittest.TestCase):
    def test_extract_comment_header(self):
        data = """# foo bar
        some other text
        """

        res = utils.extract_comment_header(StringIO(data))
        self.assertEqual(res, "foo bar")

        data = """# more
        # foobar
        some other text
        """

        res = utils.extract_comment_header(StringIO(data))
        self.assertEqual(res, "more\nfoobar")

        data = """# foo
        #  indented
        some other text
        """

        res = utils.extract_comment_header(StringIO(data))
        self.assertEqual(res, "foo\n indented")

        data = """#empty lines
        #
        #
        some other text
        """
        res = utils.extract_comment_header(StringIO(data))
        self.assertEqual(res, "empty lines")
