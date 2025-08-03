import unittest

from preparse.core import Group, Order, PreParser


class TestGroupMaximizeEdgeCases(unittest.TestCase):

    def parse(self, *, optdict, query, order=Order.GIVEN):
        p = PreParser(order=order, group=Group.MAXIMIZE, optdict=optdict)
        ans = p.parse_args(query)
        self.assertEqual(list(ans), list(p.parse_args(ans)))
        return ans

    def test_combine_with_gap_due_to_argument(self):
        optdict = {"-a": 0, "-b": 1, "-c": 0, "-d": 0}
        query = ["-a", "-b", "value", "-cd"]
        solution = ["-ab", "value", "-cd"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_do_not_combine_across_double_dash(self):
        optdict = {"-a": 0, "-b": 0, "-c": 0}
        query = ["-a", "--", "-b", "-c"]
        solution = ["-a", "--", "-b", "-c"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_combine_after_permute(self):
        optdict = {"-x": 0, "-y": 0, "-z": 0}
        query = ["file.txt", "-x", "-y", "-z"]
        solution = ["-xyz", "file.txt"]
        answer = self.parse(optdict=optdict, query=query, order=Order.PERMUTE)
        self.assertEqual(solution, answer)

    def test_preserve_mixed_grouping_and_single(self):
        optdict = {"-m": 0, "-n": 0, "-o": 0}
        query = ["-m", "-no"]
        solution = ["-mno"]
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)

    def test_merge_respects_optional_args(self):
        optdict = {"-a": 0, "-b": 2, "-c": 0}
        query = ["-a", "-bopt", "-c"]
        solution = ["-abopt", "-c"]  # -b consumes opt
        answer = self.parse(optdict=optdict, query=query)
        self.assertEqual(solution, answer)


if __name__ == "__main__":
    unittest.main()
