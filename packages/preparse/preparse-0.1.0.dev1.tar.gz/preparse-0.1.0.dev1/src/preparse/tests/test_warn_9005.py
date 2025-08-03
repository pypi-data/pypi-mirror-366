import unittest
from typing import *

from preparse.core import *


class holder:
    pass


class CustomPreParser(PreParser):
    def warnAboutUnrecognizedOption(self, option):
        holder.test.assertEqual(option, holder.option)


class TestPreParserCustomWarnings(unittest.TestCase):

    def test_custom_unrecognized_option_handler(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--unknown"
        parser.optdict = {"--foo": 1, "--bar": 1, "-x": 0}
        query = ["--unknown", "value", "--foo", "bar"]
        parser.parse_args(query)


if __name__ == "__main__":
    unittest.main()
