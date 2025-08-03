import unittest

from preparse.core import Group, Order, PreParser


class TestGroupMaximize(unittest.TestCase):

    def parse(self, *, optdict, query, order=Order.GIVEN):
        p = PreParser(order=order, group=Group.MAXIMIZE, optdict=optdict)
        ans = p.parse_args(query)
        self.assertEqual(list(ans), list(p.parse_args(ans)))
        return ans

    def test_basic_maximize_grouping(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0}
        query = ["-a", "-b", "-c"]
        solution = ["-abc"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_mixed_with_non_groupable_due_to_argument(self):
        optdict = {"-a": 0, "-b": 1, "-c": 0}
        query = ["-a", "-b", "val", "-c"]
        solution = ["-ab", "val", "-c"]  # no further grouping due to -b needing arg
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouping_across_permuted_positionals(self):
        optdict = {"-x": 0, "-y": 0, "-z": 0}
        query = ["arg1", "-x", "-y", "arg2", "-z"]
        solution = ["-xyz", "arg1", "arg2"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_grouping_stops_due_to_optional_arg(self):
        optdict = {"-a": 0, "-b": 2, "-c": 0}
        query = ["-a", "-b", "-c"]
        solution = ["-ab", "-c"]  # b has optional arg, cannot group
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouping_preserved_if_possible(self):
        optdict = {"-f": 0, "-g": 0, "-h": 0}
        query = ["-f", "-g"]
        solution = ["-fg"]  # compacted
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouping_multiple_clusters(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0, "-x": 0, "-y": 0}
        query = ["-a", "-b", "-c", "arg", "-x", "-y"]
        solution = ["-abcxy", "arg"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_grouping_multiple_clusters_given(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0, "-x": 0, "-y": 0}
        query = ["-a", "-b", "-c", "arg", "-x", "-y"]
        solution = ["-abc", "arg", "-xy"]
        answer = self.parse(optdict=optdict, query=query, order=Order.GIVEN)
        self.assertEqual(solution, answer)

    def test_grouping_multiple_clusters_posix(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0, "-x": 0, "-y": 0}
        query = ["-a", "-b", "-c", "arg", "-x", "-y"]
        solution = ["-abc", "arg", "-x", "-y"]
        answer = self.parse(optdict=optdict, query=query, order=Order.POSIX)
        self.assertEqual(solution, answer)

    def test_cannot_group_across_required_arg(self):
        optdict = {"-m": 0, "-n": 1, "-o": 0}
        query = ["-m", "-n", "data", "-o"]
        solution = ["-mn", "data", "-o"]  # -n prevents grouping
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_grouping_with_double_dash(self):
        optdict = {"-a": 0, "-b": 0}
        query = ["-a", "--", "-b"]
        solution = ["-a", "--", "-b"]  # grouping not done past "--"
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_preserve_original_if_only_one(self):
        optdict = {"-q": 0}
        query = ["-q"]
        solution = ["-q"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)


if __name__ == "__main__":
    unittest.main()
