import unittest
from typing import *

from preparse.core import *


# Holder class for temporary storage during tests
class holder:
    pass


# Custom PreParser with overridden warning methods
class CustomPreParser(PreParser):
    def warnAboutUnrecognizedOption(self, option):
        holder.test.assertEqual(option, holder.option)

    def warnAboutInvalidOption(self, option):
        holder.test.assertEqual(option, holder.option)

    def warnAboutAmbiguousOption(self, option, possibilities):
        holder.test.assertEqual(option, holder.option)
        holder.test.assertListEqual(list(possibilities), holder.possibilities)

    def warnAboutUnallowedArgument(self, option):
        holder.test.assertEqual(option, holder.option)

    def warnAboutRequiredArgument(self, option):
        holder.test.assertEqual(option, holder.option)


class TestPreParserCustomWarnings(unittest.TestCase):

    def test_custom_unrecognized_option_handler(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--unknown"
        parser.optdict = {"--foo": 1, "--bar": 1, "-x": 0}
        query = ["--unknown", "value", "--foo", "bar"]
        parser.parse_args(query)

    def test_custom_invalid_option_handler(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "z"  # Testing short option without the `-` prefix as expected
        parser.optdict = {"--foo": 1, "--bar": 1, "-x": 0}
        query = ["-z", "--foo", "value"]
        parser.parse_args(query)

    def test_custom_ambiguous_option_handler(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--fo"
        holder.possibilities = ["--foo", "--foobar", "--foxtrot"]
        parser.optdict = {"--foo": 1, "--foobar": 1, "--foxtrot": 1}
        query = ["--fo"]
        parser.parse_args(query)

    def test_custom_unallowed_argument_handler(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--flag"
        parser.optdict = {"--flag": 0, "-x": 0}
        query = ["--flag=value", "-x"]
        parser.parse_args(query)

    def test_custom_required_argument_handler(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--foo"
        parser.optdict = {"--foo": 1, "--bar": 0}
        query = ["--foo"]
        parser.parse_args(query)


if __name__ == "__main__":
    unittest.main()
