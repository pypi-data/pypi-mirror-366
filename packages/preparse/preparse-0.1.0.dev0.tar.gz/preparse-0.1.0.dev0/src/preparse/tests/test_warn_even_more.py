import unittest
import warnings as wrn

from preparse.core import *


def warn(warning: Warning) -> None:
    wrn.warn(warning)


class TestPreParserWarnings(unittest.TestCase):

    def parse_with_warning(self, optdict, query):
        """Helper method to parse args and catch warnings."""
        parser = PreParser(order=Order.PERMUTE, optdict=optdict, warn=warn)
        with wrn.catch_warnings(record=True) as w:
            wrn.simplefilter("always")
            parser.parse_args(query)
            return w

    def test_warn_about_unrecognized_option(self):
        optdict = {"--foo": 1, "--bar": 1, "-x": 0}
        query = ["--unknown", "value", "--foo", "bar"]

        warnings_caught = self.parse_with_warning(optdict, query)
        self.assertTrue(
            any(
                "unrecognized option '--unknown'" in str(warning.message)
                for warning in warnings_caught
            )
        )

    def test_warn_about_invalid_option(self):
        optdict = {"--foo": 1, "--bar": 1, "-x": 0}
        query = ["-z", "--foo", "value"]

        warnings_caught = self.parse_with_warning(optdict, query)
        self.assertTrue(
            any(
                "invalid option -- 'z'" in str(warning.message)
                for warning in warnings_caught
            )
        )

    def test_warn_about_ambiguous_option(self):
        optdict = {"--foo": 1, "--foobar": 1, "--foxtrot": 1}
        query = ["--fo"]

        warnings_caught = self.parse_with_warning(optdict, query)
        self.assertTrue(
            any(
                "option '--fo' is ambiguous; possibilities: '--foo' '--foobar' '--foxtrot'"
                in str(warning.message)
                for warning in warnings_caught
            )
        )

    def test_warn_about_unallowed_argument(self):
        optdict = {"--flag": 0, "-x": 0}
        query = ["--flag=value", "-x"]

        warnings_caught = self.parse_with_warning(optdict, query)
        self.assertTrue(
            any(
                "option '--flag' doesn't allow an argument" in str(warning.message)
                for warning in warnings_caught
            )
        )

    def test_warn_about_required_argument(self):
        optdict = {"--foo": 1, "--bar": 0}
        query = ["--foo"]

        warnings_caught = self.parse_with_warning(optdict, query)
        self.assertTrue(
            any(
                "option requires an argument -- '--foo'" in str(warning.message)
                for warning in warnings_caught
            )
        )


if __name__ == "__main__":
    unittest.main()
