import unittest

from preparse.core import Group, Order, PreParser


class TestMinimizeGroupParsing(unittest.TestCase):

    def parse(self, *, optdict, query):
        p = PreParser(order=Order.GIVEN, group=Group.MINIMIZE, optdict=optdict)
        ans = p.parse_args(query)
        self.assertEqual(list(ans), list(p.parse_args(ans)))  # round-trip check
        return ans

    def test_basic_grouping(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abc"]), ["-a", "-b", "-c"]
        )

    def test_last_option_takes_argument(self):
        optdict = {"-a": 0, "-b": 0, "-c": 1}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abcval"]), ["-a", "-b", "-cval"]
        )

    def test_argument_in_middle(self):
        optdict = {"-a": 0, "-b": 1, "-c": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abvalc"]), ["-a", "-bvalc"]
        )

    def test_unknown_short_option_warning_behavior(self):
        optdict = {"-a": 0, "-b": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abx"]), ["-a", "-b", "-x"]
        )

    def test_equals_sign_treated_as_value(self):
        optdict = {"-a": 0, "-b": 0, "-c": 1}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abc=foo"]), ["-a", "-b", "-c=foo"]
        )

    def test_mixed_grouped_and_separate_options(self):
        optdict = {"-a": 0, "-b": 1, "-v": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-av", "-bvalue"]),
            ["-a", "-v", "-bvalue"],
        )

    def test_long_option_untouched(self):
        optdict = {"-x": 0, "--file": 1}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-x", "--file=data.txt"]),
            ["-x", "--file=data.txt"],
        )

    def test_option_with_dash_value(self):
        optdict = {"-c": 1}
        self.assertEqual(self.parse(optdict=optdict, query=["-c-value"]), ["-c-value"])

    def test_double_dash_terminator(self):
        optdict = {"-a": 0, "-b": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-ab", "--", "-c"]),
            ["-a", "-b", "--", "-c"],
        )

    def test_grouped_with_space_after(self):
        optdict = {"-x": 1, "-y": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-xy", "val"]), ["-xy", "val"]
        )

    def test_grouped_option_last_requires_arg_followed_by_space(self):
        optdict = {"-a": 0, "-b": 0, "-c": 1}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abc", "VAL"]),
            ["-a", "-b", "-c", "VAL"],
        )

    def test_unrecognized_grouped_mix(self):
        optdict = {"-a": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abc"]), ["-a", "-b", "-c"]
        )

    def test_repeated_group_flags(self):
        optdict = {"-v": 0, "-d": 0}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-vv", "-dd"]), ["-v", "-v", "-d", "-d"]
        )

    def test_combined_behavior_argument_and_unknown(self):
        optdict = {"-a": 0, "-b": 1}
        self.assertEqual(
            self.parse(optdict=optdict, query=["-abvalue", "-c"]),
            ["-a", "-bvalue", "-c"],
        )


if __name__ == "__main__":
    unittest.main()
