import unittest

from preparse.core import *


class TestPreparse(unittest.TestCase):

    def test_abbrev_enum(self):
        self.assertEqual(Abbr.REJECT, 0)
        self.assertEqual(Abbr.KEEP, 1)
        self.assertEqual(Abbr.COMPLETE, 2)

    def test_nargs_enum(self):
        self.assertEqual(Nargs.NO_ARGUMENT, 0)
        self.assertEqual(Nargs.REQUIRED_ARGUMENT, 1)
        self.assertEqual(Nargs.OPTIONAL_ARGUMENT, 2)

    def test_preparser_copy(self):
        parser = PreParser()
        parser_copy = parser.copy()
        self.assertEqual(parser.abbr, parser_copy.abbr)
        self.assertEqual(parser.order, parser_copy.order)
        self.assertEqual(parser.optdict, parser_copy.optdict)

    def test_preparser_parse_args(self):
        parser = PreParser()
        mock_args = ["--option", "value"]
        result = parser.parse_args(mock_args)
        self.assertEqual(result, mock_args)

    def test_preparser_todict(self):
        parser = PreParser()
        result = parser.todict()
        expected_keys = [
            "abbr",
            "optdict",
            "order",
            "prog",
        ]
        self.assertTrue(all(key in result for key in expected_keys))

    def test_preparser_click_decorator(self):
        parser = PreParser()
        click_decorator = parser.click()
        self.assertIsInstance(click_decorator, Click)
        self.assertTrue(click_decorator.cmd)
        self.assertTrue(click_decorator.ctx)
        self.assertEqual(click_decorator.parser, parser)


if __name__ == "__main__":
    unittest.main()
