import unittest
from typing import *

from preparse.core import *


# Temporary holder class for sharing data between the test cases and the custom parser
class holder:
    pass


# Custom PreParser with overridden warning methods for testing
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

    # Unrecognized Option Tests
    def test_custom_unrecognized_option_handler_single_option(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--unknown"
        parser.optdict = {"--foo": 1, "--bar": 1, "-x": 0}
        query = ["--unknown", "value", "--foo", "bar"]
        parser.parse_args(query)

    def test_custom_unrecognized_option_handler_multiple_unrecognized(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--mystery"
        parser.optdict = {"--alpha": 1, "--beta": 1, "-y": 0}
        query = ["--mystery", "data", "--alpha", "test"]
        parser.parse_args(query)

    # Invalid Option Tests
    def test_custom_invalid_option_handler_single_invalid(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "z"  # Only the letter is expected
        parser.optdict = {"--foo": 1, "--bar": 1, "-x": 0}
        query = ["-z", "--foo", "value"]
        parser.parse_args(query)

    def test_custom_invalid_option_handler_with_combined_short_options(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "y"  # 'y' is not recognized among combined options
        parser.optdict = {"-a": 0, "-b": 0, "-c": 0}
        query = ["-abcy"]
        parser.parse_args(query)

    # Ambiguous Option Tests
    def test_custom_ambiguous_option_handler_with_partial_match(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--fo"
        holder.possibilities = ["--foo", "--foobar", "--foxtrot"]
        parser.optdict = {"--foo": 1, "--foobar": 1, "--foxtrot": 1}
        query = ["--fo"]
        parser.parse_args(query)

    def test_custom_ambiguous_option_handler_multiple_matches(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--ba"
        holder.possibilities = ["--bar", "--baz", "--bam"]
        parser.optdict = {"--bar": 1, "--baz": 1, "--bam": 1}
        query = ["--ba"]
        parser.parse_args(query)

    # Unallowed Argument Tests
    def test_custom_unallowed_argument_handler_flag_with_argument(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--flag"
        parser.optdict = {"--flag": 0, "-x": 0}
        query = ["--flag=value", "-x"]
        parser.parse_args(query)

    def test_custom_unallowed_argument_handler_combined_flags_with_argument(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "-q"
        parser.optdict = {"-q": 0, "-v": 0, "-longonly": 0}
        query = ["-q=value", "-v"]
        parser.parse_args(query)

    # Required Argument Tests
    def test_custom_required_argument_handler_missing_argument(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--foo"
        parser.optdict = {"--foo": 1, "--bar": 0}
        query = ["--foo"]
        parser.parse_args(query)

    def test_custom_required_argument_handler_multiple_required_arguments_missing(self):
        parser = CustomPreParser(order=Order.PERMUTE)
        holder.test = self
        holder.option = "--file"
        parser.optdict = {"--file": 1, "--output": 1}
        query = ["--file"]
        parser.parse_args(query)


if __name__ == "__main__":
    unittest.main()
